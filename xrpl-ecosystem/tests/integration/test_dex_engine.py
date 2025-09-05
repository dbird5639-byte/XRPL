"""
Integration tests for DEX Engine
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from core.dex_engine.engine import DEXEngine
from core.dex_engine.models import Order, Trade, OrderBook


class TestDEXEngineIntegration:
    """Integration tests for DEX Engine"""

    @pytest.fixture
    def dex_engine(self, mock_redis, mock_database):
        """Create DEX engine instance for testing."""
        with patch('core.dex_engine.engine.Redis') as mock_redis_class, \
             patch('core.dex_engine.engine.Database') as mock_db_class:
            
            mock_redis_class.return_value = mock_redis
            mock_db_class.return_value = mock_database
            
            engine = DEXEngine(
                redis_url="redis://localhost:6379",
                database_url="sqlite:///test.db"
            )
            return engine

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_place_and_cancel_order(self, dex_engine, sample_order_data):
        """Test placing and canceling an order."""
        # Place order
        order_id = await dex_engine.place_order(
            pair="XRP/USD",
            side="buy",
            type="limit",
            amount="1000.00",
            price="0.50",
            user_id="user_123"
        )
        
        assert order_id is not None
        
        # Verify order was placed
        order = await dex_engine.get_order(order_id)
        assert order is not None
        assert order.pair == "XRP/USD"
        assert order.side == "buy"
        assert order.amount == "1000.00"
        assert order.price == "0.50"
        
        # Cancel order
        result = await dex_engine.cancel_order(order_id, "user_123")
        assert result is True
        
        # Verify order was canceled
        order = await dex_engine.get_order(order_id)
        assert order.status == "cancelled"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_order_matching(self, dex_engine):
        """Test order matching functionality."""
        # Place buy order
        buy_order_id = await dex_engine.place_order(
            pair="XRP/USD",
            side="buy",
            type="limit",
            amount="1000.00",
            price="0.50",
            user_id="user_1"
        )
        
        # Place sell order
        sell_order_id = await dex_engine.place_order(
            pair="XRP/USD",
            side="sell",
            type="limit",
            amount="1000.00",
            price="0.50",
            user_id="user_2"
        )
        
        # Process matching
        trades = await dex_engine.process_matching("XRP/USD")
        
        assert len(trades) == 1
        trade = trades[0]
        assert trade.buy_order_id == buy_order_id
        assert trade.sell_order_id == sell_order_id
        assert trade.amount == "1000.00"
        assert trade.price == "0.50"
        
        # Verify orders are filled
        buy_order = await dex_engine.get_order(buy_order_id)
        sell_order = await dex_engine.get_order(sell_order_id)
        assert buy_order.status == "filled"
        assert sell_order.status == "filled"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_partial_fill(self, dex_engine):
        """Test partial order filling."""
        # Place buy order for 1000 XRP
        buy_order_id = await dex_engine.place_order(
            pair="XRP/USD",
            side="buy",
            type="limit",
            amount="1000.00",
            price="0.50",
            user_id="user_1"
        )
        
        # Place sell order for 500 XRP
        sell_order_id = await dex_engine.place_order(
            pair="XRP/USD",
            side="sell",
            type="limit",
            amount="500.00",
            price="0.50",
            user_id="user_2"
        )
        
        # Process matching
        trades = await dex_engine.process_matching("XRP/USD")
        
        assert len(trades) == 1
        trade = trades[0]
        assert trade.amount == "500.00"
        
        # Verify partial fill
        buy_order = await dex_engine.get_order(buy_order_id)
        sell_order = await dex_engine.get_order(sell_order_id)
        assert buy_order.status == "partially_filled"
        assert buy_order.filled_amount == "500.00"
        assert sell_order.status == "filled"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_order_book_updates(self, dex_engine):
        """Test order book updates."""
        # Place multiple orders
        await dex_engine.place_order(
            pair="XRP/USD",
            side="buy",
            type="limit",
            amount="1000.00",
            price="0.49",
            user_id="user_1"
        )
        
        await dex_engine.place_order(
            pair="XRP/USD",
            side="buy",
            type="limit",
            amount="2000.00",
            price="0.48",
            user_id="user_2"
        )
        
        await dex_engine.place_order(
            pair="XRP/USD",
            side="sell",
            type="limit",
            amount="1500.00",
            price="0.51",
            user_id="user_3"
        )
        
        # Get order book
        order_book = await dex_engine.get_order_book("XRP/USD")
        
        assert len(order_book.bids) == 2
        assert len(order_book.asks) == 1
        
        # Verify bid ordering (highest price first)
        assert order_book.bids[0].price == "0.49"
        assert order_book.bids[1].price == "0.48"
        
        # Verify ask ordering (lowest price first)
        assert order_book.asks[0].price == "0.51"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_market_orders(self, dex_engine):
        """Test market order execution."""
        # Place limit sell order
        sell_order_id = await dex_engine.place_order(
            pair="XRP/USD",
            side="sell",
            type="limit",
            amount="1000.00",
            price="0.50",
            user_id="user_1"
        )
        
        # Place market buy order
        buy_order_id = await dex_engine.place_order(
            pair="XRP/USD",
            side="buy",
            type="market",
            amount="500.00",
            user_id="user_2"
        )
        
        # Process matching
        trades = await dex_engine.process_matching("XRP/USD")
        
        assert len(trades) == 1
        trade = trades[0]
        assert trade.price == "0.50"  # Market order should match at limit price
        
        # Verify orders
        buy_order = await dex_engine.get_order(buy_order_id)
        sell_order = await dex_engine.get_order(sell_order_id)
        assert buy_order.status == "filled"
        assert sell_order.status == "partially_filled"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_stop_orders(self, dex_engine):
        """Test stop order functionality."""
        # Place stop buy order
        stop_order_id = await dex_engine.place_order(
            pair="XRP/USD",
            side="buy",
            type="stop",
            amount="1000.00",
            price="0.55",  # Stop price
            user_id="user_1"
        )
        
        # Place limit sell order to trigger stop
        sell_order_id = await dex_engine.place_order(
            pair="XRP/USD",
            side="sell",
            type="limit",
            amount="1000.00",
            price="0.54",
            user_id="user_2"
        )
        
        # Process matching
        trades = await dex_engine.process_matching("XRP/USD")
        
        # Stop order should be triggered and executed
        assert len(trades) == 1
        trade = trades[0]
        assert trade.buy_order_id == stop_order_id
        assert trade.sell_order_id == sell_order_id

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_user_order_history(self, dex_engine):
        """Test user order history retrieval."""
        user_id = "user_123"
        
        # Place multiple orders
        order1 = await dex_engine.place_order(
            pair="XRP/USD",
            side="buy",
            type="limit",
            amount="1000.00",
            price="0.50",
            user_id=user_id
        )
        
        order2 = await dex_engine.place_order(
            pair="XRP/BTC",
            side="sell",
            type="limit",
            amount="500.00",
            price="0.00001",
            user_id=user_id
        )
        
        # Get user orders
        orders = await dex_engine.get_user_orders(user_id)
        
        assert len(orders) == 2
        order_ids = [order.id for order in orders]
        assert order1 in order_ids
        assert order2 in order_ids

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_trade_history(self, dex_engine):
        """Test trade history retrieval."""
        # Place and match orders
        buy_order_id = await dex_engine.place_order(
            pair="XRP/USD",
            side="buy",
            type="limit",
            amount="1000.00",
            price="0.50",
            user_id="user_1"
        )
        
        sell_order_id = await dex_engine.place_order(
            pair="XRP/USD",
            side="sell",
            type="limit",
            amount="1000.00",
            price="0.50",
            user_id="user_2"
        )
        
        # Process matching
        trades = await dex_engine.process_matching("XRP/USD")
        
        # Get trade history
        trade_history = await dex_engine.get_trade_history("XRP/USD")
        
        assert len(trade_history) == 1
        trade = trade_history[0]
        assert trade.buy_order_id == buy_order_id
        assert trade.sell_order_id == sell_order_id

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_price_aggregation(self, dex_engine):
        """Test price aggregation across multiple orders."""
        # Place multiple orders at different prices
        await dex_engine.place_order(
            pair="XRP/USD",
            side="buy",
            type="limit",
            amount="1000.00",
            price="0.49",
            user_id="user_1"
        )
        
        await dex_engine.place_order(
            pair="XRP/USD",
            side="buy",
            type="limit",
            amount="2000.00",
            price="0.49",
            user_id="user_2"
        )
        
        # Get order book
        order_book = await dex_engine.get_order_book("XRP/USD")
        
        # Verify price aggregation
        assert len(order_book.bids) == 1
        bid = order_book.bids[0]
        assert bid.price == "0.49"
        assert bid.amount == "3000.00"  # Aggregated amount

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_handling(self, dex_engine):
        """Test error handling in order operations."""
        # Test invalid order parameters
        with pytest.raises(ValueError):
            await dex_engine.place_order(
                pair="INVALID/PAIR",
                side="buy",
                type="limit",
                amount="1000.00",
                price="0.50",
                user_id="user_1"
            )
        
        # Test negative amount
        with pytest.raises(ValueError):
            await dex_engine.place_order(
                pair="XRP/USD",
                side="buy",
                type="limit",
                amount="-1000.00",
                price="0.50",
                user_id="user_1"
            )
        
        # Test invalid price
        with pytest.raises(ValueError):
            await dex_engine.place_order(
                pair="XRP/USD",
                side="buy",
                type="limit",
                amount="1000.00",
                price="0.00",
                user_id="user_1"
            )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_orders(self, dex_engine):
        """Test handling concurrent order placement."""
        # Place multiple orders concurrently
        tasks = []
        for i in range(10):
            task = dex_engine.place_order(
                pair="XRP/USD",
                side="buy" if i % 2 == 0 else "sell",
                type="limit",
                amount="100.00",
                price=f"0.{50 + i}",
                user_id=f"user_{i}"
            )
            tasks.append(task)
        
        order_ids = await asyncio.gather(*tasks)
        
        # Verify all orders were placed
        assert len(order_ids) == 10
        assert all(order_id is not None for order_id in order_ids)
        
        # Verify order book has all orders
        order_book = await dex_engine.get_order_book("XRP/USD")
        total_orders = len(order_book.bids) + len(order_book.asks)
        assert total_orders == 10
