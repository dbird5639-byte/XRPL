#!/usr/bin/env python3
"""
XRPL DEX Trading Engine
Advanced decentralized exchange functionality with order book and AMM support
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import heapq

from core.xrpl_client import XRPLClient, XRPLAccount
from config import DEX_CONFIG

logger = logging.getLogger(__name__)

class OrderType(Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class OrderSide(Enum):
    """Order sides"""
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    """Order statuses"""
    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class Order:
    """Order representation"""
    id: str
    user_address: str
    side: OrderSide
    order_type: OrderType
    base_currency: str
    quote_currency: str
    base_amount: Decimal
    quote_amount: Decimal
    price: Optional[Decimal] = None
    filled_amount: Decimal = Decimal('0')
    remaining_amount: Decimal = Decimal('0')
    status: OrderStatus = OrderStatus.PENDING
    timestamp: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    stop_price: Optional[Decimal] = None
    take_profit_price: Optional[Decimal] = None
    
    def __post_init__(self):
        if self.remaining_amount == Decimal('0'):
            self.remaining_amount = self.base_amount

@dataclass
class Trade:
    """Trade representation"""
    id: str
    base_currency: str
    quote_currency: str
    base_amount: Decimal
    quote_amount: Decimal
    price: Decimal
    maker_order_id: str
    taker_order_id: str
    maker_address: str
    taker_address: str
    timestamp: float = field(default_factory=time.time)
    fee: Decimal = Decimal('0')

@dataclass
class OrderBookLevel:
    """Order book level representation"""
    price: Decimal
    total_amount: Decimal
    order_count: int
    orders: List[Order] = field(default_factory=list)

class OrderBook:
    """Order book implementation with efficient matching"""
    
    def __init__(self, base_currency: str, quote_currency: str):
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        
        # Buy orders (descending price) - highest price first
        self.buy_orders: List[OrderBookLevel] = []
        # Sell orders (ascending price) - lowest price first
        self.sell_orders: List[OrderBookLevel] = []
        
        # Order lookup by ID
        self.orders: Dict[str, Order] = {}
        
        # Price levels lookup
        self.buy_levels: Dict[Decimal, OrderBookLevel] = {}
        self.sell_levels: Dict[Decimal, OrderBookLevel] = {}
    
    def add_order(self, order: Order) -> bool:
        """Add order to order book"""
        if order.id in self.orders:
            logger.warning(f"Order {order.id} already exists")
            return False
        
        self.orders[order.id] = order
        
        if order.side == OrderSide.BUY:
            self._add_buy_order(order)
        else:
            self._add_sell_order(order)
        
        return True
    
    def _add_buy_order(self, order: Order):
        """Add buy order to order book"""
        price = order.price
        if price not in self.buy_levels:
            level = OrderBookLevel(price, Decimal('0'), 0)
            self.buy_levels[price] = level
            heapq.heappush(self.buy_orders, (-price, level))
        
        level = self.buy_levels[price]
        level.total_amount += order.remaining_amount
        level.order_count += 1
        level.orders.append(order)
    
    def _add_sell_order(self, order: Order):
        """Add sell order to order book"""
        price = order.price
        if price not in self.sell_levels:
            level = OrderBookLevel(price, Decimal('0'), 0)
            self.sell_levels[price] = level
            heapq.heappush(self.sell_orders, (price, level))
        
        level = self.sell_levels[price]
        level.total_amount += order.remaining_amount
        level.order_count += 1
        level.orders.append(order)
    
    def remove_order(self, order_id: str) -> bool:
        """Remove order from order book"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        del self.orders[order_id]
        
        if order.side == OrderSide.BUY:
            self._remove_buy_order(order)
        else:
            self._remove_sell_order(order)
        
        return True
    
    def _remove_buy_order(self, order: Order):
        """Remove buy order from order book"""
        price = order.price
        if price in self.buy_levels:
            level = self.buy_levels[price]
            level.total_amount -= order.remaining_amount
            level.order_count -= 1
            level.orders.remove(order)
            
            if level.order_count == 0:
                del self.buy_levels[price]
                # Remove from heap (this is simplified - in production you'd need more sophisticated heap management)
    
    def _remove_sell_order(self, order: Order):
        """Remove sell order from order book"""
        price = order.price
        if price in self.sell_levels:
            level = self.sell_levels[price]
            level.total_amount -= order.remaining_amount
            level.order_count -= 1
            level.orders.remove(order)
            
            if level.order_count == 0:
                del self.sell_levels[price]
    
    def get_best_bid(self) -> Optional[Decimal]:
        """Get best bid price"""
        if not self.buy_orders:
            return None
        return -self.buy_orders[0][0]  # Negative because we store as negative for max heap
    
    def get_best_ask(self) -> Optional[Decimal]:
        """Get best ask price"""
        if not self.sell_orders:
            return None
        return self.sell_orders[0][0]
    
    def get_spread(self) -> Optional[Decimal]:
        """Get current spread"""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        
        if best_bid and best_ask:
            return best_ask - best_bid
        return None
    
    def get_order_book_snapshot(self, depth: int = 10) -> Dict[str, List]:
        """Get order book snapshot"""
        bids = []
        asks = []
        
        # Get top bids
        for i, (neg_price, level) in enumerate(self.buy_orders[:depth]):
            bids.append({
                'price': float(-neg_price),
                'amount': float(level.total_amount),
                'count': level.order_count
            })
        
        # Get top asks
        for i, (price, level) in enumerate(self.sell_orders[:depth]):
            asks.append({
                'price': float(price),
                'amount': float(level.total_amount),
                'count': level.order_count
            })
        
        return {
            'bids': bids,
            'asks': asks,
            'timestamp': time.time()
        }

class DEXTradingEngine:
    """Main DEX trading engine"""
    
    def __init__(self, xrpl_client: XRPLClient):
        self.xrpl_client = xrpl_client
        self.order_books: Dict[str, OrderBook] = {}
        self.trades: List[Trade] = []
        self.users: Dict[str, Dict[str, Decimal]] = {}  # user -> currency -> balance
        
        # Trading pairs
        self.trading_pairs: List[Tuple[str, str]] = []
        
        # Fee structure
        self.fee_structure = DEX_CONFIG.fee_structure
        
        # Order ID counter
        self.order_id_counter = 0
    
    def add_trading_pair(self, base_currency: str, quote_currency: str):
        """Add a new trading pair"""
        pair_key = f"{base_currency}_{quote_currency}"
        if pair_key not in self.order_books:
            self.order_books[pair_key] = OrderBook(base_currency, quote_currency)
            self.trading_pairs.append((base_currency, quote_currency))
            logger.info(f"Added trading pair: {base_currency}/{quote_currency}")
    
    def _generate_order_id(self) -> str:
        """Generate unique order ID"""
        self.order_id_counter += 1
        return f"order_{self.order_id_counter}_{int(time.time())}"
    
    def _generate_trade_id(self) -> str:
        """Generate unique trade ID"""
        return f"trade_{int(time.time())}_{len(self.trades)}"
    
    async def place_order(
        self,
        user_address: str,
        side: OrderSide,
        order_type: OrderType,
        base_currency: str,
        quote_currency: str,
        base_amount: Union[float, Decimal],
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        take_profit_price: Optional[float] = None
    ) -> Optional[Order]:
        """Place a new order"""
        try:
            # Validate trading pair
            pair_key = f"{base_currency}_{quote_currency}"
            if pair_key not in self.order_books:
                raise ValueError(f"Trading pair {base_currency}/{quote_currency} not supported")
            
            # Convert to Decimal
            base_amount = Decimal(str(base_amount))
            price = Decimal(str(price)) if price else None
            stop_price = Decimal(str(stop_price)) if stop_price else None
            take_profit_price = Decimal(str(take_profit_price)) if take_profit_price else None
            
            # Validate order
            if base_amount <= 0:
                raise ValueError("Base amount must be positive")
            
            if order_type == OrderType.LIMIT and not price:
                raise ValueError("Price required for limit orders")
            
            if order_type in [OrderType.STOP_LOSS, OrderType.TAKE_PROFIT] and not stop_price:
                raise ValueError("Stop price required for stop orders")
            
            # Calculate quote amount
            quote_amount = base_amount * price if price else Decimal('0')
            
            # Check user balance
            if not await self._check_user_balance(user_address, base_currency, base_amount, side):
                raise ValueError("Insufficient balance")
            
            # Create order
            order = Order(
                id=self._generate_order_id(),
                user_address=user_address,
                side=side,
                order_type=order_type,
                base_currency=base_currency,
                quote_currency=quote_currency,
                base_amount=base_amount,
                quote_amount=quote_amount,
                price=price,
                stop_price=stop_price,
                take_profit_price=take_profit_price
            )
            
            # Add to order book
            if self.order_books[pair_key].add_order(order):
                # Reserve balance
                await self._reserve_balance(user_address, base_currency, base_amount, side)
                
                # Try to match immediately
                await self._try_match_orders(pair_key)
                
                logger.info(f"Order placed: {order.id} - {side.value} {base_amount} {base_currency} @ {price}")
                return order
            else:
                raise ValueError("Failed to add order to order book")
                
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None
    
    async def cancel_order(self, user_address: str, order_id: str) -> bool:
        """Cancel an existing order"""
        try:
            # Find order
            order = None
            for pair_key, order_book in self.order_books.items():
                if order_id in order_book.orders:
                    order = order_book.orders[order_id]
                    break
            
            if not order:
                raise ValueError("Order not found")
            
            if order.user_address != user_address:
                raise ValueError("Cannot cancel another user's order")
            
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
                raise ValueError("Order cannot be cancelled")
            
            # Remove from order book
            for pair_key, order_book in self.order_books.items():
                if order_book.remove_order(order_id):
                    # Release reserved balance
                    await self._release_balance(user_address, order.base_currency, order.remaining_amount, order.side)
                    
                    # Update order status
                    order.status = OrderStatus.CANCELLED
                    
                    logger.info(f"Order cancelled: {order_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
            return False
    
    async def _try_match_orders(self, pair_key: str):
        """Try to match orders in the order book"""
        order_book = self.order_books[pair_key]
        
        while True:
            best_bid = order_book.get_best_bid()
            best_ask = order_book.get_best_ask()
            
            # Check if orders can be matched
            if not best_bid or not best_ask or best_bid < best_ask:
                break
            
            # Get orders at best prices
            bid_level = order_book.buy_levels[best_bid]
            ask_level = order_book.sell_levels[best_ask]
            
            if not bid_level.orders or not ask_level.orders:
                break
            
            # Match orders
            bid_order = bid_level.orders[0]
            ask_order = ask_level.orders[0]
            
            # Calculate trade amount
            trade_amount = min(bid_order.remaining_amount, ask_order.remaining_amount)
            trade_price = best_bid  # Use bid price for matching
            
            # Execute trade
            await self._execute_trade(bid_order, ask_order, trade_amount, trade_price, pair_key)
            
            # Check if orders are fully filled
            if bid_order.remaining_amount == 0:
                bid_order.status = OrderStatus.FILLED
                order_book.remove_order(bid_order.id)
            
            if ask_order.remaining_amount == 0:
                ask_order.status = OrderStatus.FILLED
                order_book.remove_order(ask_order.id)
    
    async def _execute_trade(
        self,
        bid_order: Order,
        ask_order: Order,
        amount: Decimal,
        price: Decimal,
        pair_key: str
    ):
        """Execute a trade between two orders"""
        try:
            # Calculate amounts
            quote_amount = amount * price
            
            # Calculate fees
            bid_fee = amount * self.fee_structure["taker"]
            ask_fee = amount * self.fee_structure["taker"]
            
            # Create trade record
            trade = Trade(
                id=self._generate_trade_id(),
                base_currency=bid_order.base_currency,
                quote_currency=bid_order.quote_currency,
                base_amount=amount,
                quote_amount=quote_amount,
                price=price,
                maker_order_id=ask_order.id,
                taker_order_id=bid_order.id,
                maker_address=ask_order.user_address,
                taker_address=bid_order.user_address,
                fee=bid_fee + ask_fee
            )
            
            self.trades.append(trade)
            
            # Update order amounts
            bid_order.filled_amount += amount
            bid_order.remaining_amount -= amount
            ask_order.filled_amount += amount
            ask_order.remaining_amount -= amount
            
            # Update user balances
            await self._update_balances_after_trade(
                bid_order, ask_order, amount, quote_amount, bid_fee, ask_fee
            )
            
            logger.info(f"Trade executed: {trade.id} - {amount} {bid_order.base_currency} @ {price}")
            
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
    
    async def _check_user_balance(
        self,
        user_address: str,
        currency: str,
        amount: Decimal,
        side: OrderSide
    ) -> bool:
        """Check if user has sufficient balance"""
        if user_address not in self.users:
            self.users[user_address] = {}
        
        user_balance = self.users[user_address].get(currency, Decimal('0'))
        
        if side == OrderSide.BUY:
            # For buy orders, check quote currency balance
            return user_balance >= amount
        else:
            # For sell orders, check base currency balance
            return user_balance >= amount
    
    async def _reserve_balance(
        self,
        user_address: str,
        currency: str,
        amount: Decimal,
        side: OrderSide
    ):
        """Reserve balance for an order"""
        if user_address not in self.users:
            self.users[user_address] = {}
        
        if currency not in self.users[user_address]:
            self.users[user_address][currency] = Decimal('0')
        
        # Reserve the balance
        self.users[user_address][currency] -= amount
    
    async def _release_balance(
        self,
        user_address: str,
        currency: str,
        amount: Decimal,
        side: OrderSide
    ):
        """Release reserved balance"""
        if user_address in self.users and currency in self.users[user_address]:
            self.users[user_address][currency] += amount
    
    async def _update_balances_after_trade(
        self,
        bid_order: Order,
        ask_order: Order,
        amount: Decimal,
        quote_amount: Decimal,
        bid_fee: Decimal,
        ask_fee: Decimal
    ):
        """Update user balances after a trade"""
        # Update bid order user (buyer)
        if bid_order.user_address not in self.users:
            self.users[bid_order.user_address] = {}
        
        # Buyer receives base currency, pays quote currency
        self.users[bid_order.user_address][bid_order.base_currency] = \
            self.users[bid_order.user_address].get(bid_order.base_currency, Decimal('0')) + amount
        
        self.users[bid_order.user_address][bid_order.quote_currency] = \
            self.users[bid_order.user_address].get(bid_order.quote_currency, Decimal('0')) - quote_amount - bid_fee
        
        # Update ask order user (seller)
        if ask_order.user_address not in self.users:
            self.users[ask_order.user_address] = {}
        
        # Seller receives quote currency, pays base currency
        self.users[ask_order.user_address][bid_order.quote_currency] = \
            self.users[ask_order.user_address].get(bid_order.quote_currency, Decimal('0')) + quote_amount - ask_fee
        
        self.users[ask_order.user_address][bid_order.base_currency] = \
            self.users[ask_order.user_address].get(bid_order.base_currency, Decimal('0')) - amount
    
    def get_user_orders(self, user_address: str) -> List[Order]:
        """Get all orders for a user"""
        orders = []
        for order_book in self.order_books.values():
            for order in order_book.orders.values():
                if order.user_address == user_address:
                    orders.append(order)
        return orders
    
    def get_user_trades(self, user_address: str) -> List[Trade]:
        """Get all trades for a user"""
        return [trade for trade in self.trades 
                if trade.maker_address == user_address or trade.taker_address == user_address]
    
    def get_order_book(self, base_currency: str, quote_currency: str, depth: int = 20) -> Optional[Dict]:
        """Get order book for a trading pair"""
        pair_key = f"{base_currency}_{quote_currency}"
        if pair_key in self.order_books:
            return self.order_books[pair_key].get_order_book_snapshot(depth)
        return None
    
    def get_trading_pairs(self) -> List[Tuple[str, str]]:
        """Get list of available trading pairs"""
        return self.trading_pairs.copy()
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get market summary for all trading pairs"""
        summary = {}
        
        for base, quote in self.trading_pairs:
            pair_key = f"{base}_{quote}"
            order_book = self.order_books[pair_key]
            
            best_bid = order_book.get_best_bid()
            best_ask = order_book.get_best_ask()
            spread = order_book.get_spread()
            
            summary[pair_key] = {
                'base_currency': base,
                'quote_currency': quote,
                'best_bid': float(best_bid) if best_bid else None,
                'best_ask': float(best_ask) if best_ask else None,
                'spread': float(spread) if spread else None,
                'bid_volume': float(order_book.buy_levels[best_bid].total_amount) if best_bid else 0,
                'ask_volume': float(order_book.sell_levels[best_ask].total_amount) if best_ask else 0
            }
        
        return summary
