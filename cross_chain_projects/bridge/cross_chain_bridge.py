#!/usr/bin/env python3
"""
Cross-Chain Bridge Module
Enables seamless asset transfers between XRPL and other blockchains
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import json

from web3 import Web3
from solana.rpc.async_api import AsyncClient as SolanaClient
from solana.transaction import Transaction
from solana.keypair import Keypair
from solana.publickey import PublicKey

from core.xrpl_client import XRPLClient, XRPLAccount
from config import BRIDGE_CONFIG

logger = logging.getLogger(__name__)

class BridgeStatus(Enum):
    """Bridge transaction status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BridgeDirection(Enum):
    """Bridge direction"""
    XRPL_TO_ETH = "xrpl_to_eth"
    ETH_TO_XRPL = "eth_to_xrpl"
    XRPL_TO_SOL = "xrpl_to_sol"
    SOL_TO_XRPL = "sol_to_xrpl"
    XRPL_TO_POLYGON = "xrpl_to_polygon"
    POLYGON_TO_XRPL = "polygon_to_xrpl"

@dataclass
class BridgeTransaction:
    """Bridge transaction representation"""
    id: str
    user_address: str
    direction: BridgeDirection
    source_chain: str
    destination_chain: str
    source_currency: str
    destination_currency: str
    amount: Decimal
    destination_amount: Decimal
    fee: Decimal
    status: BridgeStatus
    source_tx_hash: Optional[str] = None
    destination_tx_hash: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    error_message: Optional[str] = None

@dataclass
class BridgeConfig:
    """Bridge configuration for a specific chain"""
    rpc_url: str
    bridge_contract: str
    gas_limit: int
    gas_price: Optional[int] = None
    confirmations_required: int = 12
    timeout_seconds: int = 3600

class CrossChainBridge:
    """Main cross-chain bridge implementation"""
    
    def __init__(self, xrpl_client: XRPLClient):
        self.xrpl_client = xrpl_client
        
        # Initialize blockchain clients
        self.ethereum_client = None
        self.solana_client = None
        self.polygon_client = None
        
        # Bridge configurations
        self.bridge_configs: Dict[str, BridgeConfig] = {}
        
        # Transaction tracking
        self.bridge_transactions: Dict[str, BridgeTransaction] = {}
        
        # Initialize bridge
        self._init_bridge()
    
    def _init_bridge(self):
        """Initialize bridge connections and configurations"""
        try:
            # Ethereum bridge
            if BRIDGE_CONFIG.ethereum_rpc:
                self.ethereum_client = Web3(Web3.HTTPProvider(BRIDGE_CONFIG.ethereum_rpc))
                self.bridge_configs["ethereum"] = BridgeConfig(
                    rpc_url=BRIDGE_CONFIG.ethereum_rpc,
                    bridge_contract=BRIDGE_CONFIG.ethereum_bridge,
                    gas_limit=500000,
                    confirmations_required=12
                )
                logger.info("Ethereum bridge initialized")
            
            # Solana bridge
            if BRIDGE_CONFIG.solana_rpc:
                self.solana_client = SolanaClient(BRIDGE_CONFIG.solana_rpc)
                self.bridge_configs["solana"] = BridgeConfig(
                    rpc_url=BRIDGE_CONFIG.solana_rpc,
                    bridge_contract=BRIDGE_CONFIG.solana_bridge,
                    gas_limit=0,  # Solana doesn't use gas
                    confirmations_required=32
                )
                logger.info("Solana bridge initialized")
            
            # Polygon bridge
            if BRIDGE_CONFIG.polygon_rpc:
                self.polygon_client = Web3(Web3.HTTPProvider(BRIDGE_CONFIG.polygon_rpc))
                self.bridge_configs["polygon"] = BridgeConfig(
                    rpc_url=BRIDGE_CONFIG.polygon_rpc,
                    bridge_contract=BRIDGE_CONFIG.polygon_bridge,
                    gas_limit=300000,
                    confirmations_required=8
                )
                logger.info("Polygon bridge initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize bridge: {e}")
    
    async def bridge_asset(
        self,
        user_address: str,
        direction: BridgeDirection,
        amount: Union[float, Decimal],
        source_currency: str,
        destination_currency: str,
        destination_address: str
    ) -> Optional[str]:
        """Initiate asset bridge between chains"""
        try:
            # Validate direction
            if not self._validate_bridge_direction(direction):
                raise ValueError(f"Unsupported bridge direction: {direction}")
            
            # Convert amount to Decimal
            amount = Decimal(str(amount))
            
            # Calculate fees and destination amount
            fee = self._calculate_bridge_fee(amount, direction)
            destination_amount = amount - fee
            
            # Validate amounts
            if destination_amount <= 0:
                raise ValueError("Amount too small to cover bridge fees")
            
            # Create bridge transaction
            bridge_tx = BridgeTransaction(
                id=self._generate_bridge_id(),
                user_address=user_address,
                direction=direction,
                source_chain=self._get_source_chain(direction),
                destination_chain=self._get_destination_chain(direction),
                source_currency=source_currency,
                destination_currency=destination_currency,
                amount=amount,
                destination_amount=destination_amount,
                fee=fee,
                status=BridgeStatus.PENDING
            )
            
            # Store transaction
            self.bridge_transactions[bridge_tx.id] = bridge_tx
            
            # Process bridge based on direction
            if direction in [BridgeDirection.XRPL_TO_ETH, BridgeDirection.XRPL_TO_SOL, BridgeDirection.XRPL_TO_POLYGON]:
                await self._process_xrpl_to_external(bridge_tx, destination_address)
            else:
                await self._process_external_to_xrpl(bridge_tx, destination_address)
            
            logger.info(f"Bridge transaction initiated: {bridge_tx.id}")
            return bridge_tx.id
            
        except Exception as e:
            logger.error(f"Failed to initiate bridge: {e}")
            return None
    
    def _validate_bridge_direction(self, direction: BridgeDirection) -> bool:
        """Validate if bridge direction is supported"""
        supported_directions = [
            BridgeDirection.XRPL_TO_ETH,
            BridgeDirection.ETH_TO_XRPL,
            BridgeDirection.XRPL_TO_SOL,
            BridgeDirection.SOL_TO_XRPL,
            BridgeDirection.XRPL_TO_POLYGON,
            BridgeDirection.POLYGON_TO_XRPL
        ]
        return direction in supported_directions
    
    def _calculate_bridge_fee(self, amount: Decimal, direction: BridgeDirection) -> Decimal:
        """Calculate bridge fee based on amount and direction"""
        # Base fee + percentage fee
        base_fee = Decimal('0.001')  # 0.1%
        percentage_fee = amount * Decimal('0.005')  # 0.5%
        
        # Add chain-specific fees
        if "ethereum" in direction.value:
            percentage_fee += amount * Decimal('0.002')  # Additional 0.2% for ETH gas
        elif "solana" in direction.value:
            percentage_fee += amount * Decimal('0.001')  # Additional 0.1% for Solana
        
        return base_fee + percentage_fee
    
    def _get_source_chain(self, direction: BridgeDirection) -> str:
        """Get source chain from bridge direction"""
        if direction.value.startswith("xrpl_to"):
            return "xrpl"
        elif direction.value.endswith("_to_xrpl"):
            if "eth" in direction.value:
                return "ethereum"
            elif "sol" in direction.value:
                return "solana"
            elif "polygon" in direction.value:
                return "polygon"
        return "unknown"
    
    def _get_destination_chain(self, direction: BridgeDirection) -> str:
        """Get destination chain from bridge direction"""
        if direction.value.endswith("_to_xrpl"):
            return "xrpl"
        elif direction.value.startswith("xrpl_to"):
            if "eth" in direction.value:
                return "ethereum"
            elif "sol" in direction.value:
                return "solana"
            elif "polygon" in direction.value:
                return "polygon"
        return "unknown"
    
    def _generate_bridge_id(self) -> str:
        """Generate unique bridge transaction ID"""
        return f"bridge_{int(time.time())}_{len(self.bridge_transactions)}"
    
    async def _process_xrpl_to_external(
        self,
        bridge_tx: BridgeTransaction,
        destination_address: str
    ):
        """Process bridge from XRPL to external chain"""
        try:
            # Update status
            bridge_tx.status = BridgeStatus.PROCESSING
            
            # Lock XRPL assets (this would typically involve escrow)
            # For now, we'll simulate this
            logger.info(f"Locking {bridge_tx.amount} {bridge_tx.source_currency} on XRPL")
            
            # Process on destination chain based on type
            if bridge_tx.destination_chain == "ethereum":
                await self._process_ethereum_deposit(bridge_tx, destination_address)
            elif bridge_tx.destination_chain == "solana":
                await self._process_solana_deposit(bridge_tx, destination_address)
            elif bridge_tx.destination_chain == "polygon":
                await self._process_polygon_deposit(bridge_tx, destination_address)
            
        except Exception as e:
            logger.error(f"Failed to process XRPL to external bridge: {e}")
            bridge_tx.status = BridgeStatus.FAILED
            bridge_tx.error_message = str(e)
    
    async def _process_external_to_xrpl(
        self,
        bridge_tx: BridgeTransaction,
        destination_address: str
    ):
        """Process bridge from external chain to XRPL"""
        try:
            # Update status
            bridge_tx.status = BridgeStatus.PROCESSING
            
            # Process on source chain based on type
            if bridge_tx.source_chain == "ethereum":
                await self._process_ethereum_withdrawal(bridge_tx, destination_address)
            elif bridge_tx.source_chain == "solana":
                await self._process_solana_withdrawal(bridge_tx, destination_address)
            elif bridge_tx.source_chain == "polygon":
                await self._process_polygon_withdrawal(bridge_tx, destination_address)
            
        except Exception as e:
            logger.error(f"Failed to process external to XRPL bridge: {e}")
            bridge_tx.status = BridgeStatus.FAILED
            bridge_tx.error_message = str(e)
    
    async def _process_ethereum_deposit(
        self,
        bridge_tx: BridgeTransaction,
        destination_address: str
    ):
        """Process Ethereum deposit for bridge"""
        try:
            if not self.ethereum_client:
                raise ValueError("Ethereum client not initialized")
            
            # This would typically involve calling the bridge contract
            # For now, we'll simulate the process
            logger.info(f"Processing Ethereum deposit for {bridge_tx.destination_amount} {bridge_tx.destination_currency}")
            
            # Simulate contract call
            await asyncio.sleep(2)  # Simulate processing time
            
            # Update transaction
            bridge_tx.destination_tx_hash = f"eth_tx_{int(time.time())}"
            bridge_tx.status = BridgeStatus.COMPLETED
            bridge_tx.completed_at = time.time()
            
            logger.info(f"Ethereum deposit completed: {bridge_tx.id}")
            
        except Exception as e:
            logger.error(f"Failed to process Ethereum deposit: {e}")
            bridge_tx.status = BridgeStatus.FAILED
            bridge_tx.error_message = str(e)
    
    async def _process_solana_deposit(
        self,
        bridge_tx: BridgeTransaction,
        destination_address: str
    ):
        """Process Solana deposit for bridge"""
        try:
            if not self.solana_client:
                raise ValueError("Solana client not initialized")
            
            # This would typically involve calling the bridge program
            logger.info(f"Processing Solana deposit for {bridge_tx.destination_amount} {bridge_tx.destination_currency}")
            
            # Simulate program call
            await asyncio.sleep(1.5)  # Simulate processing time
            
            # Update transaction
            bridge_tx.destination_tx_hash = f"sol_tx_{int(time.time())}"
            bridge_tx.status = BridgeStatus.COMPLETED
            bridge_tx.completed_at = time.time()
            
            logger.info(f"Solana deposit completed: {bridge_tx.id}")
            
        except Exception as e:
            logger.error(f"Failed to process Solana deposit: {e}")
            bridge_tx.status = BridgeStatus.FAILED
            bridge_tx.error_message = str(e)
    
    async def _process_polygon_deposit(
        self,
        bridge_tx: BridgeTransaction,
        destination_address: str
    ):
        """Process Polygon deposit for bridge"""
        try:
            if not self.polygon_client:
                raise ValueError("Polygon client not initialized")
            
            # This would typically involve calling the bridge contract
            logger.info(f"Processing Polygon deposit for {bridge_tx.destination_amount} {bridge_tx.destination_currency}")
            
            # Simulate contract call
            await asyncio.sleep(1)  # Simulate processing time
            
            # Update transaction
            bridge_tx.destination_tx_hash = f"poly_tx_{int(time.time())}"
            bridge_tx.status = BridgeStatus.COMPLETED
            bridge_tx.completed_at = time.time()
            
            logger.info(f"Polygon deposit completed: {bridge_tx.id}")
            
        except Exception as e:
            logger.error(f"Failed to process Polygon deposit: {e}")
            bridge_tx.status = BridgeStatus.FAILED
            bridge_tx.error_message = str(e)
    
    async def _process_ethereum_withdrawal(
        self,
        bridge_tx: BridgeTransaction,
        destination_address: str
    ):
        """Process Ethereum withdrawal for bridge"""
        try:
            if not self.ethereum_client:
                raise ValueError("Ethereum client not initialized")
            
            # This would typically involve monitoring the bridge contract
            logger.info(f"Processing Ethereum withdrawal for {bridge_tx.amount} {bridge_tx.source_currency}")
            
            # Simulate monitoring
            await asyncio.sleep(3)  # Simulate processing time
            
            # Update transaction
            bridge_tx.source_tx_hash = f"eth_tx_{int(time.time())}"
            bridge_tx.status = BridgeStatus.COMPLETED
            bridge_tx.completed_at = time.time()
            
            logger.info(f"Ethereum withdrawal completed: {bridge_tx.id}")
            
        except Exception as e:
            logger.error(f"Failed to process Ethereum withdrawal: {e}")
            bridge_tx.status = BridgeStatus.FAILED
            bridge_tx.error_message = str(e)
    
    async def _process_solana_withdrawal(
        self,
        bridge_tx: BridgeTransaction,
        destination_address: str
    ):
        """Process Solana withdrawal for bridge"""
        try:
            if not self.solana_client:
                raise ValueError("Solana client not initialized")
            
            # This would typically involve monitoring the bridge program
            logger.info(f"Processing Solana withdrawal for {bridge_tx.amount} {bridge_tx.source_currency}")
            
            # Simulate monitoring
            await asyncio.sleep(2)  # Simulate processing time
            
            # Update transaction
            bridge_tx.source_tx_hash = f"sol_tx_{int(time.time())}"
            bridge_tx.status = BridgeStatus.COMPLETED
            bridge_tx.completed_at = time.time()
            
            logger.info(f"Solana withdrawal completed: {bridge_tx.id}")
            
        except Exception as e:
            logger.error(f"Failed to process Solana withdrawal: {e}")
            bridge_tx.status = BridgeStatus.FAILED
            bridge_tx.error_message = str(e)
    
    async def _process_polygon_withdrawal(
        self,
        bridge_tx: BridgeTransaction,
        destination_address: str
    ):
        """Process Polygon withdrawal for bridge"""
        try:
            if not self.polygon_client:
                raise ValueError("Polygon client not initialized")
            
            # This would typically involve monitoring the bridge contract
            logger.info(f"Processing Polygon withdrawal for {bridge_tx.amount} {bridge_tx.source_currency}")
            
            # Simulate monitoring
            await asyncio.sleep(1.5)  # Simulate processing time
            
            # Update transaction
            bridge_tx.source_tx_hash = f"poly_tx_{int(time.time())}"
            bridge_tx.status = BridgeStatus.COMPLETED
            bridge_tx.completed_at = time.time()
            
            logger.info(f"Polygon withdrawal completed: {bridge_tx.id}")
            
        except Exception as e:
            logger.error(f"Failed to process Polygon withdrawal: {e}")
            bridge_tx.status = BridgeStatus.FAILED
            bridge_tx.error_message = str(e)
    
    def get_bridge_transaction(self, tx_id: str) -> Optional[BridgeTransaction]:
        """Get bridge transaction by ID"""
        return self.bridge_transactions.get(tx_id)
    
    def get_user_bridge_transactions(self, user_address: str) -> List[BridgeTransaction]:
        """Get all bridge transactions for a user"""
        return [tx for tx in self.bridge_transactions.values() 
                if tx.user_address == user_address]
    
    def get_bridge_status(self, tx_id: str) -> Optional[BridgeStatus]:
        """Get status of a bridge transaction"""
        tx = self.get_bridge_transaction(tx_id)
        return tx.status if tx else None
    
    def get_bridge_statistics(self) -> Dict[str, Any]:
        """Get bridge statistics"""
        total_transactions = len(self.bridge_transactions)
        completed_transactions = len([tx for tx in self.bridge_transactions.values() 
                                   if tx.status == BridgeStatus.COMPLETED])
        failed_transactions = len([tx for tx in self.bridge_transactions.values() 
                                 if tx.status == BridgeStatus.FAILED])
        pending_transactions = len([tx for tx in self.bridge_transactions.values() 
                                  if tx.status == BridgeStatus.PENDING])
        
        total_volume = sum([tx.amount for tx in self.bridge_transactions.values() 
                           if tx.status == BridgeStatus.COMPLETED])
        total_fees = sum([tx.fee for tx in self.bridge_transactions.values() 
                         if tx.status == BridgeStatus.COMPLETED])
        
        return {
            'total_transactions': total_transactions,
            'completed_transactions': completed_transactions,
            'failed_transactions': failed_transactions,
            'pending_transactions': pending_transactions,
            'success_rate': completed_transactions / total_transactions if total_transactions > 0 else 0,
            'total_volume': float(total_volume),
            'total_fees': float(total_fees),
            'supported_chains': list(self.bridge_configs.keys())
        }
    
    async def cancel_bridge_transaction(self, tx_id: str, user_address: str) -> bool:
        """Cancel a pending bridge transaction"""
        try:
            tx = self.get_bridge_transaction(tx_id)
            if not tx:
                raise ValueError("Bridge transaction not found")
            
            if tx.user_address != user_address:
                raise ValueError("Cannot cancel another user's transaction")
            
            if tx.status != BridgeStatus.PENDING:
                raise ValueError("Only pending transactions can be cancelled")
            
            # Cancel transaction
            tx.status = BridgeStatus.CANCELLED
            
            logger.info(f"Bridge transaction cancelled: {tx_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel bridge transaction: {e}")
            return False
    
    async def retry_failed_transaction(self, tx_id: str, user_address: str) -> bool:
        """Retry a failed bridge transaction"""
        try:
            tx = self.get_bridge_transaction(tx_id)
            if not tx:
                raise ValueError("Bridge transaction not found")
            
            if tx.user_address != user_address:
                raise ValueError("Cannot retry another user's transaction")
            
            if tx.status != BridgeStatus.FAILED:
                raise ValueError("Only failed transactions can be retried")
            
            # Reset transaction
            tx.status = BridgeStatus.PENDING
            tx.error_message = None
            tx.completed_at = None
            tx.source_tx_hash = None
            tx.destination_tx_hash = None
            
            # Retry processing
            if tx.direction.value.startswith("xrpl_to"):
                await self._process_xrpl_to_external(tx, tx.user_address)
            else:
                await self._process_external_to_xrpl(tx, tx.user_address)
            
            logger.info(f"Bridge transaction retried: {tx_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retry bridge transaction: {e}")
            return False
