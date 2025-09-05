#!/usr/bin/env python3
"""
XRPL Ecosystem Main Application
Main entry point for the XRPL ecosystem with all components integrated
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Any
from pathlib import Path

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

# Import our modules
from config import config
from core.xrpl_client import XRPLClient
from dex.dex_engine import DEXTradingEngine
from bridge.cross_chain_bridge import CrossChainBridge
from ai_trading.ai_trading_engine import AITradingEngine

class XRPLecosystem:
    """Main XRPL ecosystem application"""
    
    def __init__(self):
        self.running = False
        self.components = {}
        
        # Initialize components
        self._init_components()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _init_components(self):
        """Initialize all ecosystem components"""
        try:
            logger.info("Initializing XRPL Ecosystem components...")
            
            # Initialize XRPL client
            self.components['xrpl_client'] = XRPLClient(
                network=config.environment,
                use_websocket=True
            )
            
            # Initialize DEX engine
            self.components['dex_engine'] = DEXTradingEngine(
                self.components['xrpl_client']
            )
            
            # Initialize cross-chain bridge
            self.components['bridge'] = CrossChainBridge(
                self.components['xrpl_client']
            )
            
            # Initialize AI trading engine
            self.components['ai_trading'] = AITradingEngine(
                self.components['xrpl_client'],
                self.components['dex_engine']
            )
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def start(self):
        """Start the XRPL ecosystem"""
        try:
            logger.info("Starting XRPL Ecosystem...")
            self.running = True
            
            # Connect to XRPL
            await self.components['xrpl_client'].connect()
            
            # Setup trading pairs
            await self._setup_trading_pairs()
            
            # Start background tasks
            await self._start_background_tasks()
            
            logger.info("XRPL Ecosystem started successfully")
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Failed to start XRPL Ecosystem: {e}")
            await self.stop()
    
    async def _setup_trading_pairs(self):
        """Setup initial trading pairs"""
        try:
            # Add common trading pairs
            trading_pairs = [
                ("XRP", "USD"),
                ("XRP", "USDT"),
                ("XRP", "BTC"),
                ("XRP", "ETH"),
                ("BTC", "USD"),
                ("ETH", "USD"),
                ("SOL", "USD"),
                ("MATIC", "USD")
            ]
            
            for base, quote in trading_pairs:
                self.components['dex_engine'].add_trading_pair(base, quote)
            
            logger.info(f"Added {len(trading_pairs)} trading pairs")
            
        except Exception as e:
            logger.error(f"Failed to setup trading pairs: {e}")
    
    async def _start_background_tasks(self):
        """Start background tasks"""
        try:
            # Start AI trading loop
            asyncio.create_task(self._ai_trading_loop())
            
            # Start portfolio update loop
            asyncio.create_task(self._portfolio_update_loop())
            
            # Start market data collection loop
            asyncio.create_task(self._market_data_loop())
            
            logger.info("Background tasks started")
            
        except Exception as e:
            logger.error(f"Failed to start background tasks: {e}")
    
    async def _ai_trading_loop(self):
        """AI trading main loop"""
        while self.running:
            try:
                # Generate trading signals
                signals = await self.components['ai_trading'].generate_signals({})
                
                if signals:
                    # Execute signals
                    executed_orders = await self.components['ai_trading'].execute_signals(signals)
                    
                    if executed_orders:
                        logger.info(f"Executed {len(executed_orders)} AI trading orders")
                
                # Wait before next iteration
                await asyncio.sleep(AI_CONFIG.prediction_interval)
                
            except Exception as e:
                logger.error(f"Error in AI trading loop: {e}")
                await asyncio.sleep(10)
    
    async def _portfolio_update_loop(self):
        """Portfolio update loop"""
        while self.running:
            try:
                # Get current market prices (simulated)
                current_prices = {
                    "XRP_USD": 0.5,
                    "XRP_USDT": 0.5,
                    "BTC_USD": 45000.0,
                    "ETH_USD": 3000.0
                }
                
                # Update portfolio
                self.components['ai_trading'].update_portfolio(current_prices)
                
                # Get portfolio metrics
                metrics = self.components['ai_trading'].get_portfolio_metrics()
                
                if metrics.total_trades > 0:
                    logger.info(f"Portfolio: ${metrics.total_value:.2f}, PnL: ${metrics.total_pnl:.2f} ({metrics.total_pnl_percentage:.2f}%)")
                
                # Wait before next update
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error in portfolio update loop: {e}")
                await asyncio.sleep(30)
    
    async def _market_data_loop(self):
        """Market data collection loop"""
        while self.running:
            try:
                # Get market summary
                market_summary = self.components['dex_engine'].get_market_summary()
                
                # Log market activity
                for pair, data in market_summary.items():
                    if data['best_bid'] and data['best_ask']:
                        spread = data['spread'] if data['spread'] else 0
                        logger.debug(f"{pair}: Bid: ${data['best_bid']:.6f}, Ask: ${data['best_ask']:.6f}, Spread: {spread:.4f}%")
                
                # Wait before next update
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in market data loop: {e}")
                await asyncio.sleep(30)
    
    async def stop(self):
        """Stop the XRPL ecosystem"""
        try:
            logger.info("Stopping XRPL Ecosystem...")
            self.running = False
            
            # Disconnect from XRPL
            if 'xrpl_client' in self.components:
                await self.components['xrpl_client'].disconnect()
            
            logger.info("XRPL Ecosystem stopped")
            
        except Exception as e:
            logger.error(f"Error stopping XRPL Ecosystem: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.stop())

async def main():
    """Main entry point"""
    try:
        # Create and start ecosystem
        ecosystem = XRPLecosystem()
        await ecosystem.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("XRPL Ecosystem shutdown complete")

if __name__ == "__main__":
    # Run the application
    asyncio.run(main())
