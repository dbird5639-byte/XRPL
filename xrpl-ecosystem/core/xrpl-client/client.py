#!/usr/bin/env python3
"""
XRPL Client Module
Core XRPL functionality for connecting, managing accounts, and handling transactions
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from decimal import Decimal

import xrpl
from xrpl.clients import JsonRpcClient, WebsocketClient
from xrpl.models import (
    AccountSet, Payment, TrustSet, OfferCreate, OfferCancel,
    AccountTx, AccountLines, AccountOffers, LedgerEntry
)
from xrpl.transaction import (
    submit_and_wait, safe_sign_and_autofill_transaction
)
from xrpl.wallet import Wallet, generate_faucet_wallet
from xrpl.utils import xrp_to_drops, drops_to_xrp

logger = logging.getLogger(__name__)

@dataclass
class XRPLAccount:
    """XRPL Account Information"""
    address: str
    public_key: str
    private_key: str
    seed: str
    sequence: int
    balance: str
    domain: Optional[str] = None
    email_hash: Optional[str] = None
    message_key: Optional[str] = None
    transfer_rate: Optional[int] = None

@dataclass
class XRPLBalance:
    """XRPL Balance Information"""
    xrp_balance: str
    token_balances: Dict[str, Dict[str, str]]
    total_value_usd: Optional[float] = None

class XRPLClient:
    """XRPL Client for managing connections and transactions"""
    
    def __init__(self, network: str = "mainnet", use_websocket: bool = True):
        self.network = network
        self.use_websocket = use_websocket
        self.client = None
        self.connected = False
        self._connection_lock = asyncio.Lock()
        
        # Network URLs
        self.network_urls = {
            "mainnet": "wss://xrplcluster.com",
            "testnet": "wss://s.altnet.rippletest.net:51233",
            "devnet": "wss://s.devnet.rippletest.net:51233",
            "amm_devnet": "wss://amm.devnet.rippletest.net:51233"
        }
        
        # Initialize client
        self._init_client()
    
    def _init_client(self):
        """Initialize the appropriate XRPL client"""
        if self.network not in self.network_urls:
            raise ValueError(f"Unsupported network: {self.network}")
        
        url = self.network_urls[self.network]
        
        if self.use_websocket:
            self.client = WebsocketClient(url)
        else:
            self.client = JsonRpcClient(url)
    
    async def connect(self) -> bool:
        """Connect to XRPL network"""
        async with self._connection_lock:
            if self.connected:
                return True
            
            try:
                if self.use_websocket:
                    await self.client.open()
                self.connected = True
                logger.info(f"Connected to XRPL {self.network}")
                return True
            except Exception as e:
                logger.error(f"Failed to connect to XRPL {self.network}: {e}")
                self.connected = False
                return False
    
    async def disconnect(self):
        """Disconnect from XRPL network"""
        async with self._connection_lock:
            if not self.connected:
                return
            
            try:
                if self.use_websocket:
                    await self.client.close()
                self.connected = False
                logger.info(f"Disconnected from XRPL {self.network}")
            except Exception as e:
                logger.error(f"Error disconnecting from XRPL {self.network}: {e}")
    
    async def get_account_info(self, address: str) -> Optional[Dict[str, Any]]:
        """Get account information"""
        if not await self.connect():
            return None
        
        try:
            response = await self.client.request(
                xrpl.models.AccountInfo(account=address, ledger_index="validated")
            )
            return response.result.get("account_data")
        except Exception as e:
            logger.error(f"Failed to get account info for {address}: {e}")
            return None
    
    async def get_account_balance(self, address: str) -> Optional[XRPLBalance]:
        """Get account balance including XRP and tokens"""
        account_info = await self.get_account_info(address)
        if not account_info:
            return None
        
        try:
            # Get XRP balance
            xrp_balance = account_info.get("Balance", "0")
            
            # Get token balances
            token_balances = {}
            account_lines = await self.get_account_lines(address)
            if account_lines:
                for line in account_lines:
                    currency = line.get("currency")
                    if currency:
                        token_balances[currency] = {
                            "balance": line.get("balance", "0"),
                            "limit": line.get("limit", "0"),
                            "limit_peer": line.get("limit_peer", "0"),
                            "quality_in": line.get("quality_in", "0"),
                            "quality_out": line.get("quality_out", "0")
                        }
            
            return XRPLBalance(
                xrp_balance=xrp_balance,
                token_balances=token_balances
            )
        except Exception as e:
            logger.error(f"Failed to get account balance for {address}: {e}")
            return None
    
    async def get_account_lines(self, address: str) -> Optional[List[Dict[str, Any]]]:
        """Get account trust lines (token balances)"""
        if not await self.connect():
            return None
        
        try:
            response = await self.client.request(
                AccountLines(account=address, ledger_index="validated")
            )
            return response.result.get("lines", [])
        except Exception as e:
            logger.error(f"Failed to get account lines for {address}: {e}")
            return None
    
    async def get_account_offers(self, address: str) -> Optional[List[Dict[str, Any]]]:
        """Get account offers"""
        if not await self.connect():
            return None
        
        try:
            response = await self.client.request(
                AccountOffers(account=address, ledger_index="validated")
            )
            return response.result.get("offers", [])
        except Exception as e:
            logger.error(f"Failed to get account offers for {address}: {e}")
            return None
    
    async def get_account_transactions(self, address: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """Get account transaction history"""
        if not await self.connect():
            return None
        
        try:
            response = await self.client.request(
                AccountTx(account=address, limit=limit)
            )
            return response.result.get("transactions", [])
        except Exception as e:
            logger.error(f"Failed to get account transactions for {address}: {e}")
            return None
    
    async def create_wallet(self) -> Optional[XRPLAccount]:
        """Create a new XRPL wallet"""
        try:
            if self.network in ["testnet", "devnet", "amm_devnet"]:
                wallet = generate_faucet_wallet(self.client)
            else:
                wallet = Wallet.create()
            
            # Get account info
            account_info = await self.get_account_info(wallet.classic_address)
            if account_info:
                return XRPLAccount(
                    address=wallet.classic_address,
                    public_key=wallet.public_key,
                    private_key=wallet.private_key,
                    seed=wallet.seed,
                    sequence=account_info.get("Sequence", 0),
                    balance=account_info.get("Balance", "0")
                )
            return None
        except Exception as e:
            logger.error(f"Failed to create wallet: {e}")
            return None
    
    async def send_payment(
        self,
        wallet: XRPLAccount,
        destination: str,
        amount: Union[str, float],
        currency: str = "XRP",
        issuer: Optional[str] = None
    ) -> Optional[str]:
        """Send payment transaction"""
        if not await self.connect():
            return None
        
        try:
            # Prepare payment transaction
            if currency == "XRP":
                if isinstance(amount, float):
                    amount = xrp_to_drops(amount)
                payment_tx = Payment(
                    account=wallet.address,
                    destination=destination,
                    amount=amount
                )
            else:
                # Token payment
                if not issuer:
                    raise ValueError(f"Issuer required for token payment: {currency}")
                
                payment_tx = Payment(
                    account=wallet.address,
                    destination=destination,
                    amount={
                        "currency": currency,
                        "issuer": issuer,
                        "value": str(amount)
                    }
                )
            
            # Sign and submit transaction
            signed_tx = safe_sign_and_autofill_transaction(
                payment_tx, wallet, self.client
            )
            
            response = await submit_and_wait(signed_tx, self.client)
            
            if response.is_successful():
                logger.info(f"Payment successful: {response.result.get('hash')}")
                return response.result.get("hash")
            else:
                logger.error(f"Payment failed: {response.result}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to send payment: {e}")
            return None
    
    async def create_offer(
        self,
        wallet: XRPLAccount,
        taker_gets: Union[str, Dict[str, Any]],
        taker_pays: Union[str, Dict[str, Any]],
        flags: int = 0
    ) -> Optional[str]:
        """Create a new offer"""
        if not await self.connect():
            return None
        
        try:
            offer_tx = OfferCreate(
                account=wallet.address,
                taker_gets=taker_gets,
                taker_pays=taker_pays,
                flags=flags
            )
            
            # Sign and submit transaction
            signed_tx = safe_sign_and_autofill_transaction(
                offer_tx, wallet, self.client
            )
            
            response = await submit_and_wait(signed_tx, self.client)
            
            if response.is_successful():
                logger.info(f"Offer created: {response.result.get('hash')}")
                return response.result.get("hash")
            else:
                logger.error(f"Offer creation failed: {response.result}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create offer: {e}")
            return None
    
    async def cancel_offer(
        self,
        wallet: XRPLAccount,
        offer_sequence: int
    ) -> Optional[str]:
        """Cancel an existing offer"""
        if not await self.connect():
            return None
        
        try:
            cancel_tx = OfferCancel(
                account=wallet.address,
                offer_sequence=offer_sequence
            )
            
            # Sign and submit transaction
            signed_tx = safe_sign_and_autofill_transaction(
                cancel_tx, wallet, self.client
            )
            
            response = await submit_and_wait(signed_tx, self.client)
            
            if response.is_successful():
                logger.info(f"Offer cancelled: {response.result.get('hash')}")
                return response.result.get("hash")
            else:
                logger.error(f"Offer cancellation failed: {response.result}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to cancel offer: {e}")
            return None
    
    async def set_trust_line(
        self,
        wallet: XRPLAccount,
        currency: str,
        issuer: str,
        limit: str = "0"
    ) -> Optional[str]:
        """Set trust line for a token"""
        if not await self.connect():
            return None
        
        try:
            trust_tx = TrustSet(
                account=wallet.address,
                limit_amount={
                    "currency": currency,
                    "issuer": issuer,
                    "value": limit
                }
            )
            
            # Sign and submit transaction
            signed_tx = safe_sign_and_autofill_transaction(
                trust_tx, wallet, self.client
            )
            
            response = await submit_and_wait(signed_tx, self.client)
            
            if response.is_successful():
                logger.info(f"Trust line set: {response.result.get('hash')}")
                return response.result.get("hash")
            else:
                logger.error(f"Trust line setting failed: {response.result}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to set trust line: {e}")
            return None
    
    async def get_ledger_info(self) -> Optional[Dict[str, Any]]:
        """Get current ledger information"""
        if not await self.connect():
            return None
        
        try:
            response = await self.client.request(
                xrpl.models.Ledger(ledger_index="validated")
            )
            return response.result.get("ledger")
        except Exception as e:
            logger.error(f"Failed to get ledger info: {e}")
            return None
    
    async def get_transaction_info(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction information by hash"""
        if not await self.connect():
            return None
        
        try:
            response = await self.client.request(
                xrpl.models.Tx(transaction=tx_hash)
            )
            return response.result
        except Exception as e:
            logger.error(f"Failed to get transaction info for {tx_hash}: {e}")
            return None
