"""
DEX Trading Engine Models
Data models for orders, trades, and order book
"""

import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

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
