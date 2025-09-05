#!/usr/bin/env python3
"""
Basic Usage Example
Demonstrates how to use the XRPL ecosystem components
"""

import asyncio
import logging
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def basic_xrpl_example():
    """Basic XRPL functionality example"""
    try:
        from core.xrpl_client import XRPLClient
        
        # Create XRPL client (using testnet for safety)
        client = XRPLClient(network="testnet")
        
        # Connect to XRPL
        await client.connect()
        logger.info("Connected to XRPL testnet")
        
        # Create a new wallet
        wallet = await client.create_wallet()
        if wallet:
            logger.info(f"Created wallet: {wallet.address}")
            logger.info(f"Seed: {wallet.seed}")
            logger.info(f"Balance: {wallet.balance}")
        
        # Get ledger info
        ledger_info = await client.get_ledger_info()
        if ledger_info:
            logger.info(f"Current ledger: {ledger_info.get('ledger_index')}")
        
        # Disconnect
        await client.disconnect()
        logger.info("Disconnected from XRPL")
        
    except Exception as e:
        logger.error(f"Error in basic XRPL example: {e}")

async def dex_trading_example():
    """DEX trading example"""
    try:
        from core.xrpl_client import XRPLClient
        from dex.dex_engine import DEXTradingEngine, OrderSide, OrderType
        
        # Create XRPL client
        client = XRPLClient(network="testnet")
        await client.connect()
        
        # Create DEX engine
        dex = DEXTradingEngine(client)
        
        # Add trading pair
        dex.add_trading_pair("XRP", "USD")
        logger.info("Added XRP/USD trading pair")
        
        # Get order book
        order_book = dex.get_order_book("XRP", "USD")
        if order_book:
            logger.info(f"Order book: {order_book}")
        
        # Get market summary
        market_summary = dex.get_market_summary()
        logger.info(f"Market summary: {market_summary}")
        
        await client.disconnect()
        
    except Exception as e:
        logger.error(f"Error in DEX trading example: {e}")

async def cross_chain_bridge_example():
    """Cross-chain bridge example"""
    try:
        from core.xrpl_client import XRPLClient
        from bridge.cross_chain_bridge import CrossChainBridge, BridgeDirection
        
        # Create XRPL client
        client = XRPLClient(network="testnet")
        await client.connect()
        
        # Create bridge
        bridge = CrossChainBridge(client)
        
        # Get bridge statistics
        stats = bridge.get_bridge_statistics()
        logger.info(f"Bridge statistics: {stats}")
        
        # Get supported chains
        supported_chains = bridge.bridge_configs.keys()
        logger.info(f"Supported chains: {list(supported_chains)}")
        
        await client.disconnect()
        
    except Exception as e:
        logger.error(f"Error in cross-chain bridge example: {e}")

async def ai_trading_example():
    """AI trading example"""
    try:
        from core.xrpl_client import XRPLClient
        from dex.dex_engine import DEXTradingEngine
        from ai_trading.ai_trading_engine import AITradingEngine
        
        # Create XRPL client
        client = XRPLClient(network="testnet")
        await client.connect()
        
        # Create DEX engine
        dex = DEXTradingEngine(client)
        
        # Create AI trading engine
        ai_trading = AITradingEngine(client, dex)
        
        # Get available models
        available_models = list(ai_trading.models.keys())
        logger.info(f"Available AI models: {available_models}")
        
        # Get strategy configurations
        strategies = list(ai_trading.strategy_configs.keys())
        logger.info(f"Available strategies: {strategies}")
        
        await client.disconnect()
        
    except Exception as e:
        logger.error(f"Error in AI trading example: {e}")

async def portfolio_management_example():
    """Portfolio management example"""
    try:
        from core.xrpl_client import XRPLClient
        from dex.dex_engine import DEXTradingEngine
        from ai_trading.ai_trading_engine import AITradingEngine
        
        # Create components
        client = XRPLClient(network="testnet")
        await client.connect()
        
        dex = DEXTradingEngine(client)
        ai_trading = AITradingEngine(client, dex)
        
        # Add some trading pairs
        dex.add_trading_pair("XRP", "USD")
        dex.add_trading_pair("BTC", "USD")
        
        # Simulate some market data
        current_prices = {
            "XRP_USD": 0.5,
            "BTC_USD": 45000.0
        }
        
        # Update portfolio
        ai_trading.update_portfolio(current_prices)
        
        # Get portfolio metrics
        metrics = ai_trading.get_portfolio_metrics()
        logger.info(f"Portfolio metrics: {metrics}")
        
        # Get open positions
        open_positions = ai_trading.get_open_positions()
        logger.info(f"Open positions: {len(open_positions)}")
        
        await client.disconnect()
        
    except Exception as e:
        logger.error(f"Error in portfolio management example: {e}")

async def main():
    """Run all examples"""
    logger.info("Starting XRPL Ecosystem Examples")
    
    try:
        # Run examples
        await basic_xrpl_example()
        await dex_trading_example()
        await cross_chain_bridge_example()
        await ai_trading_example()
        await portfolio_management_example()
        
        logger.info("All examples completed successfully")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")

if __name__ == "__main__":
    asyncio.run(main())
