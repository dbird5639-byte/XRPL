#!/usr/bin/env python3
"""
XRPL Ecosystem Main Entry Point
Comprehensive XRPL ecosystem with cross-chain DEX, DeFi protocols, and innovative applications
"""

import asyncio
import logging
import sys
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.xrpl_client import XRPLClient
from core.dex_engine import DEXTradingEngine
from core.bridge_engine import CrossChainBridge, NetworkType
from core.security import FortKnoxSecurity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xrpl_ecosystem.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class XRPLEcosystem:
    """Main XRPL Ecosystem orchestrator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.xrpl_client = None
        self.dex_engine = None
        self.bridge_engine = None
        self.security_system = None
        self.running = False
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all ecosystem components"""
        try:
            # Initialize XRPL client
            network = self.config.get('network', 'testnet')
            self.xrpl_client = XRPLClient(network=network)
            
            # Initialize DEX engine
            self.dex_engine = DEXTradingEngine(self.xrpl_client)
            
            # Initialize bridge engine
            bridge_config = self.config.get('bridge', {})
            self.bridge_engine = CrossChainBridge(bridge_config)
            
            # Initialize security system
            self.security_system = FortKnoxSecurity()
            
            logger.info("XRPL Ecosystem components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def start(self):
        """Start the XRPL ecosystem"""
        try:
            logger.info("Starting XRPL Ecosystem...")
            
            # Connect to XRPL
            if not await self.xrpl_client.connect():
                raise Exception("Failed to connect to XRPL network")
            
            # Add default trading pairs
            self._setup_default_trading_pairs()
            
            # Start background tasks
            self.running = True
            tasks = [
                asyncio.create_task(self._monitor_system_health()),
                asyncio.create_task(self._process_security_events()),
                asyncio.create_task(self._update_market_data())
            ]
            
            logger.info("XRPL Ecosystem started successfully")
            logger.info(f"Network: {self.config.get('network', 'testnet')}")
            logger.info(f"Trading pairs: {self.dex_engine.get_trading_pairs()}")
            
            # Wait for tasks to complete
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Failed to start XRPL Ecosystem: {e}")
            raise
    
    async def stop(self):
        """Stop the XRPL ecosystem"""
        try:
            logger.info("Stopping XRPL Ecosystem...")
            
            self.running = False
            
            # Disconnect from XRPL
            if self.xrpl_client:
                await self.xrpl_client.disconnect()
            
            logger.info("XRPL Ecosystem stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping XRPL Ecosystem: {e}")
    
    def _setup_default_trading_pairs(self):
        """Setup default trading pairs"""
        default_pairs = [
            ("XRP", "USD"),
            ("XRP", "USDT"),
            ("BTC", "USD"),
            ("ETH", "USD"),
            ("XRP", "BTC")
        ]
        
        for base, quote in default_pairs:
            self.dex_engine.add_trading_pair(base, quote)
        
        logger.info(f"Added {len(default_pairs)} default trading pairs")
    
    async def _monitor_system_health(self):
        """Monitor system health and performance"""
        while self.running:
            try:
                # Check XRPL connection
                if not self.xrpl_client.connected:
                    logger.warning("XRPL connection lost, attempting to reconnect...")
                    await self.xrpl_client.connect()
                
                # Check security system status
                security_status = await self.security_system.get_security_status()
                if security_status.get('emergency_mode'):
                    logger.critical("Emergency mode activated!")
                
                # Log system status
                logger.info("System health check completed")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _process_security_events(self):
        """Process security events and take appropriate actions"""
        while self.running:
            try:
                # This would process pending security events
                # For now, just log that we're monitoring
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Security event processing error: {e}")
                await asyncio.sleep(5)
    
    async def _update_market_data(self):
        """Update market data and order books"""
        while self.running:
            try:
                # This would update market data from external sources
                # For now, just log that we're updating
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Market data update error: {e}")
                await asyncio.sleep(10)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Get XRPL connection status
            xrpl_status = {
                "connected": self.xrpl_client.connected if self.xrpl_client else False,
                "network": self.config.get('network', 'testnet')
            }
            
            # Get DEX status
            dex_status = {
                "trading_pairs": len(self.dex_engine.get_trading_pairs()),
                "active_orders": sum(len(ob.orders) for ob in self.dex_engine.order_books.values()),
                "total_trades": len(self.dex_engine.trades)
            }
            
            # Get bridge status
            bridge_stats = await self.bridge_engine.get_bridge_statistics()
            
            # Get security status
            security_status = await self.security_system.get_security_status()
            
            return {
                "system": {
                    "running": self.running,
                    "uptime": "N/A",  # Would calculate actual uptime
                    "version": "1.0.0"
                },
                "xrpl": xrpl_status,
                "dex": dex_status,
                "bridge": bridge_stats,
                "security": security_status
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}
    
    async def place_order(self, user_address: str, side: str, order_type: str,
                         base_currency: str, quote_currency: str, amount: float,
                         price: Optional[float] = None) -> Optional[Dict]:
        """Place a trading order"""
        try:
            from core.dex_engine.models import OrderSide, OrderType
            
            # Convert string enums
            side_enum = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
            type_enum = OrderType.MARKET if order_type.lower() == 'market' else OrderType.LIMIT
            
            # Security analysis
            transaction_data = {
                'from_address': user_address,
                'to_address': 'DEX',
                'amount': amount,
                'currency': base_currency
            }
            
            threat_detected, actions, risk_score = await self.security_system.analyze_transaction(transaction_data)
            
            if threat_detected and SecurityAction.BLOCK in actions:
                logger.warning(f"Order blocked by security system: {user_address}")
                return None
            
            # Place order
            order = await self.dex_engine.place_order(
                user_address=user_address,
                side=side_enum,
                order_type=type_enum,
                base_currency=base_currency,
                quote_currency=quote_currency,
                base_amount=amount,
                price=price
            )
            
            if order:
                return {
                    "order_id": order.id,
                    "status": order.status.value,
                    "amount": float(order.base_amount),
                    "price": float(order.price) if order.price else None,
                    "timestamp": order.timestamp
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None
    
    async def get_order_book(self, base_currency: str, quote_currency: str) -> Optional[Dict]:
        """Get order book for a trading pair"""
        try:
            return self.dex_engine.get_order_book(base_currency, quote_currency)
        except Exception as e:
            logger.error(f"Failed to get order book: {e}")
            return None

async def main():
    """Main entry point"""
    try:
        # Configuration
        config = {
            'network': 'testnet',  # Use testnet for development
            'bridge': {
                'xrpl_rpc_url': 'wss://s.altnet.rippletest.net:51233',
                'eth_rpc_url': 'https://mainnet.infura.io/v3/your_key',
                'bsc_rpc_url': 'https://bsc-dataseed.binance.org/',
                'polygon_rpc_url': 'https://polygon-rpc.com/'
            }
        }
        
        # Create and start ecosystem
        ecosystem = XRPLEcosystem(config)
        
        # Handle graceful shutdown
        def signal_handler():
            logger.info("Received shutdown signal")
            asyncio.create_task(ecosystem.stop())
        
        # Start the ecosystem
        await ecosystem.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
