#!/usr/bin/env python3
"""
XRPL Arbitrage Bot
Automated cross-exchange price arbitrage for XRP and other tokens
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import aiohttp
import websockets
from dataclasses import dataclass
from decimal import Decimal
import hashlib
import hmac
import base64
from urllib.parse import urlencode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arbitrage_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ArbitrageOpportunity:
    """Represents an arbitrage opportunity"""
    token: str
    buy_exchange: str
    sell_exchange: str
    buy_price: Decimal
    sell_price: Decimal
    profit_percentage: Decimal
    min_profit_threshold: Decimal
    volume: Decimal
    timestamp: datetime

@dataclass
class ExchangeConfig:
    """Exchange configuration"""
    name: str
    api_key: str
    secret_key: str
    base_url: str
    websocket_url: str
    trading_fee: Decimal
    withdrawal_fee: Decimal
    min_trade_amount: Decimal
    max_trade_amount: Decimal

class XRPLArbitrageBot:
    """Main arbitrage bot class"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self.load_config(config_file)
        self.exchanges = self.setup_exchanges()
        self.opportunities: List[ArbitrageOpportunity] = []
        self.running = False
        self.balance_cache: Dict[str, Dict[str, Decimal]] = {}
        self.price_cache: Dict[str, Dict[str, Decimal]] = {}
        
        # Arbitrage parameters
        self.min_profit_threshold = Decimal(self.config.get('min_profit_threshold', '0.5'))  # 0.5%
        self.max_position_size = Decimal(self.config.get('max_position_size', '1000'))  # 1000 XRP
        self.gas_price_buffer = Decimal(self.config.get('gas_price_buffer', '1.2'))  # 20% buffer
        
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file {config_file} not found")
            return {}
    
    def setup_exchanges(self) -> Dict[str, ExchangeConfig]:
        """Setup exchange configurations"""
        exchanges = {}
        
        # Binance configuration
        if 'binance' in self.config:
            exchanges['binance'] = ExchangeConfig(
                name='binance',
                api_key=self.config['binance']['api_key'],
                secret_key=self.config['binance']['secret_key'],
                base_url='https://api.binance.com',
                websocket_url='wss://stream.binance.com:9443/ws/',
                trading_fee=Decimal('0.001'),  # 0.1%
                withdrawal_fee=Decimal('0.5'),  # 0.5 XRP
                min_trade_amount=Decimal('10'),
                max_trade_amount=Decimal('10000')
            )
        
        # Coinbase configuration
        if 'coinbase' in self.config:
            exchanges['coinbase'] = ExchangeConfig(
                name='coinbase',
                api_key=self.config['coinbase']['api_key'],
                secret_key=self.config['coinbase']['secret_key'],
                base_url='https://api.exchange.coinbase.com',
                websocket_url='wss://ws-feed.exchange.coinbase.com',
                trading_fee=Decimal('0.005'),  # 0.5%
                withdrawal_fee=Decimal('1.0'),  # 1 XRP
                min_trade_amount=Decimal('25'),
                max_trade_amount=Decimal('50000')
            )
        
        # Kraken configuration
        if 'kraken' in self.config:
            exchanges['kraken'] = ExchangeConfig(
                name='kraken',
                api_key=self.config['kraken']['api_key'],
                secret_key=self.config['kraken']['secret_key'],
                base_url='https://api.kraken.com',
                websocket_url='wss://ws.kraken.com',
                trading_fee=Decimal('0.0026'),  # 0.26%
                withdrawal_fee=Decimal('0.02'),  # 0.02 XRP
                min_trade_amount=Decimal('5'),
                max_trade_amount=Decimal('20000')
            )
        
        return exchanges
    
    async def get_price(self, exchange: str, symbol: str) -> Optional[Decimal]:
        """Get current price from exchange"""
        try:
            if exchange == 'binance':
                return await self.get_binance_price(symbol)
            elif exchange == 'coinbase':
                return await self.get_coinbase_price(symbol)
            elif exchange == 'kraken':
                return await self.get_kraken_price(symbol)
        except Exception as e:
            logger.error(f"Error getting price from {exchange}: {e}")
            return None
    
    async def get_binance_price(self, symbol: str) -> Decimal:
        """Get price from Binance"""
        url = f"{self.exchanges['binance'].base_url}/api/v3/ticker/price"
        params = {'symbol': symbol}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                return Decimal(data['price'])
    
    async def get_coinbase_price(self, symbol: str) -> Decimal:
        """Get price from Coinbase"""
        url = f"{self.exchanges['coinbase'].base_url}/products/{symbol}/ticker"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return Decimal(data['price'])
    
    async def get_kraken_price(self, symbol: str) -> Decimal:
        """Get price from Kraken"""
        url = f"{self.exchanges['kraken'].base_url}/0/public/Ticker"
        params = {'pair': symbol}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                # Kraken returns data in a different format
                pair_data = data['result'][list(data['result'].keys())[0]]
                return Decimal(pair_data['c'][0])  # Current price
    
    async def get_balance(self, exchange: str, asset: str) -> Decimal:
        """Get balance from exchange"""
        try:
            if exchange == 'binance':
                return await self.get_binance_balance(asset)
            elif exchange == 'coinbase':
                return await self.get_coinbase_balance(asset)
            elif exchange == 'kraken':
                return await self.get_kraken_balance(asset)
        except Exception as e:
            logger.error(f"Error getting balance from {exchange}: {e}")
            return Decimal('0')
    
    async def get_binance_balance(self, asset: str) -> Decimal:
        """Get balance from Binance"""
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = hmac.new(
            self.exchanges['binance'].secret_key.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        url = f"{self.exchanges['binance'].base_url}/api/v3/account"
        params = {
            'timestamp': timestamp,
            'signature': signature
        }
        
        headers = {'X-MBX-APIKEY': self.exchanges['binance'].api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                data = await response.json()
                for balance in data['balances']:
                    if balance['asset'] == asset:
                        return Decimal(balance['free'])
                return Decimal('0')
    
    async def get_coinbase_balance(self, asset: str) -> Decimal:
        """Get balance from Coinbase"""
        timestamp = str(int(time.time()))
        message = timestamp + 'GET' + '/accounts'
        signature = hmac.new(
            self.exchanges['coinbase'].secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'CB-ACCESS-KEY': self.exchanges['coinbase'].api_key,
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-PASS PHRASE': self.config['coinbase']['passphrase']
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.exchanges['coinbase'].base_url}/accounts", headers=headers) as response:
                data = await response.json()
                for account in data:
                    if account['currency'] == asset:
                        return Decimal(account['available'])
                return Decimal('0')
    
    async def get_kraken_balance(self, asset: str) -> Decimal:
        """Get balance from Kraken"""
        # Kraken API implementation would go here
        # This is a simplified version
        return Decimal('0')
    
    async def find_arbitrage_opportunities(self) -> List[ArbitrageOpportunity]:
        """Find arbitrage opportunities across exchanges"""
        opportunities = []
        symbols = ['XRPUSDT', 'XRPBTC', 'XRPETH']
        
        for symbol in symbols:
            prices = {}
            
            # Get prices from all exchanges
            for exchange_name in self.exchanges.keys():
                price = await self.get_price(exchange_name, symbol)
                if price:
                    prices[exchange_name] = price
            
            # Find arbitrage opportunities
            if len(prices) >= 2:
                sorted_prices = sorted(prices.items(), key=lambda x: x[1])
                
                for i in range(len(sorted_prices)):
                    for j in range(i + 1, len(sorted_prices)):
                        buy_exchange, buy_price = sorted_prices[i]
                        sell_exchange, sell_price = sorted_prices[j]
                        
                        profit_percentage = ((sell_price - buy_price) / buy_price) * 100
                        
                        if profit_percentage > self.min_profit_threshold:
                            opportunity = ArbitrageOpportunity(
                                token=symbol,
                                buy_exchange=buy_exchange,
                                sell_exchange=sell_exchange,
                                buy_price=buy_price,
                                sell_price=sell_price,
                                profit_percentage=profit_percentage,
                                min_profit_threshold=self.min_profit_threshold,
                                volume=Decimal('0'),  # Will be calculated based on balance
                                timestamp=datetime.now()
                            )
                            opportunities.append(opportunity)
        
        return opportunities
    
    async def execute_arbitrage(self, opportunity: ArbitrageOpportunity) -> bool:
        """Execute arbitrage trade"""
        try:
            logger.info(f"Executing arbitrage: {opportunity.token} "
                       f"Buy {opportunity.buy_exchange} @ {opportunity.buy_price} "
                       f"Sell {opportunity.sell_exchange} @ {opportunity.sell_price} "
                       f"Profit: {opportunity.profit_percentage:.2f}%")
            
            # Calculate optimal trade size
            trade_size = self.calculate_optimal_trade_size(opportunity)
            
            if trade_size < self.exchanges[opportunity.buy_exchange].min_trade_amount:
                logger.warning(f"Trade size too small: {trade_size}")
                return False
            
            # Execute buy order
            buy_success = await self.execute_buy_order(
                opportunity.buy_exchange,
                opportunity.token,
                trade_size
            )
            
            if not buy_success:
                logger.error("Buy order failed")
                return False
            
            # Execute sell order
            sell_success = await self.execute_sell_order(
                opportunity.sell_exchange,
                opportunity.token,
                trade_size
            )
            
            if not sell_success:
                logger.error("Sell order failed")
                # TODO: Implement rollback mechanism
                return False
            
            logger.info(f"Arbitrage executed successfully. Profit: {opportunity.profit_percentage:.2f}%")
            return True
            
        except Exception as e:
            logger.error(f"Error executing arbitrage: {e}")
            return False
    
    def calculate_optimal_trade_size(self, opportunity: ArbitrageOpportunity) -> Decimal:
        """Calculate optimal trade size based on available balance and risk"""
        # Get available balance from buy exchange
        available_balance = self.balance_cache.get(opportunity.buy_exchange, {}).get('USDT', Decimal('0'))
        
        # Calculate maximum trade size based on balance
        max_trade_by_balance = available_balance / opportunity.buy_price
        
        # Apply position size limits
        max_trade_by_position = self.max_position_size
        
        # Use the smaller of the two
        optimal_size = min(max_trade_by_balance, max_trade_by_position)
        
        return optimal_size
    
    async def execute_buy_order(self, exchange: str, symbol: str, amount: Decimal) -> bool:
        """Execute buy order on exchange"""
        try:
            if exchange == 'binance':
                return await self.execute_binance_buy_order(symbol, amount)
            elif exchange == 'coinbase':
                return await self.execute_coinbase_buy_order(symbol, amount)
            elif exchange == 'kraken':
                return await self.execute_kraken_buy_order(symbol, amount)
        except Exception as e:
            logger.error(f"Error executing buy order on {exchange}: {e}")
            return False
    
    async def execute_sell_order(self, exchange: str, symbol: str, amount: Decimal) -> bool:
        """Execute sell order on exchange"""
        try:
            if exchange == 'binance':
                return await self.execute_binance_sell_order(symbol, amount)
            elif exchange == 'coinbase':
                return await self.execute_coinbase_sell_order(symbol, amount)
            elif exchange == 'kraken':
                return await self.execute_kraken_sell_order(symbol, amount)
        except Exception as e:
            logger.error(f"Error executing sell order on {exchange}: {e}")
            return False
    
    async def execute_binance_buy_order(self, symbol: str, amount: Decimal) -> bool:
        """Execute buy order on Binance"""
        # Implementation would go here
        # This is a placeholder
        logger.info(f"Executing Binance buy order: {symbol} {amount}")
        return True
    
    async def execute_binance_sell_order(self, symbol: str, amount: Decimal) -> bool:
        """Execute sell order on Binance"""
        # Implementation would go here
        # This is a placeholder
        logger.info(f"Executing Binance sell order: {symbol} {amount}")
        return True
    
    async def execute_coinbase_buy_order(self, symbol: str, amount: Decimal) -> bool:
        """Execute buy order on Coinbase"""
        # Implementation would go here
        # This is a placeholder
        logger.info(f"Executing Coinbase buy order: {symbol} {amount}")
        return True
    
    async def execute_coinbase_sell_order(self, symbol: str, amount: Decimal) -> bool:
        """Execute sell order on Coinbase"""
        # Implementation would go here
        # This is a placeholder
        logger.info(f"Executing Coinbase sell order: {symbol} {amount}")
        return True
    
    async def execute_kraken_buy_order(self, symbol: str, amount: Decimal) -> bool:
        """Execute buy order on Kraken"""
        # Implementation would go here
        # This is a placeholder
        logger.info(f"Executing Kraken buy order: {symbol} {amount}")
        return True
    
    async def execute_kraken_sell_order(self, symbol: str, amount: Decimal) -> bool:
        """Execute sell order on Kraken"""
        # Implementation would go here
        # This is a placeholder
        logger.info(f"Executing Kraken sell order: {symbol} {amount}")
        return True
    
    async def update_balances(self):
        """Update balance cache"""
        for exchange_name in self.exchanges.keys():
            self.balance_cache[exchange_name] = {}
            for asset in ['XRP', 'USDT', 'BTC', 'ETH']:
                balance = await self.get_balance(exchange_name, asset)
                self.balance_cache[exchange_name][asset] = balance
    
    async def run(self):
        """Main bot loop"""
        logger.info("Starting XRPL Arbitrage Bot...")
        self.running = True
        
        while self.running:
            try:
                # Update balances
                await self.update_balances()
                
                # Find arbitrage opportunities
                opportunities = await self.find_arbitrage_opportunities()
                
                # Execute profitable opportunities
                for opportunity in opportunities:
                    if opportunity.profit_percentage > self.min_profit_threshold:
                        success = await self.execute_arbitrage(opportunity)
                        if success:
                            logger.info(f"Arbitrage executed successfully: {opportunity.profit_percentage:.2f}% profit")
                
                # Wait before next iteration
                await asyncio.sleep(5)  # 5 second intervals
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    def stop(self):
        """Stop the bot"""
        logger.info("Stopping XRPL Arbitrage Bot...")
        self.running = False

async def main():
    """Main function"""
    bot = XRPLArbitrageBot()
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        bot.stop()
    except Exception as e:
        logger.error(f"Bot error: {e}")
        bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
