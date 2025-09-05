"""
Pytest configuration and fixtures for XRPL Ecosystem tests
"""

import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
import tempfile
import shutil

# Test configuration
pytest_plugins = ["pytest_asyncio"]

# Test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def mock_xrpl_client() -> Mock:
    """Mock XRPL client for testing."""
    client = Mock()
    client.connect = AsyncMock(return_value=True)
    client.disconnect = AsyncMock(return_value=True)
    client.get_account_info = AsyncMock(return_value={
        "account": "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
        "balance": "1000000000",
        "sequence": 12345
    })
    client.get_balances = AsyncMock(return_value=[
        {"currency": "XRP", "value": "1000.000000", "issuer": None}
    ])
    client.send_payment = AsyncMock(return_value="tx_hash_123")
    return client

@pytest.fixture
def mock_dex_engine() -> Mock:
    """Mock DEX engine for testing."""
    engine = Mock()
    engine.place_order = AsyncMock(return_value="order_123")
    engine.cancel_order = AsyncMock(return_value=True)
    engine.get_order_book = AsyncMock(return_value={
        "bids": [{"price": "0.50", "amount": "1000.00"}],
        "asks": [{"price": "0.51", "amount": "1000.00"}]
    })
    engine.get_user_orders = AsyncMock(return_value=[])
    return engine

@pytest.fixture
def mock_bridge_engine() -> Mock:
    """Mock bridge engine for testing."""
    engine = Mock()
    engine.initiate_bridge = AsyncMock(return_value="bridge_123")
    engine.get_bridge_status = AsyncMock(return_value="completed")
    engine.get_bridge_history = AsyncMock(return_value=[])
    return engine

@pytest.fixture
def mock_security_system() -> Mock:
    """Mock security system for testing."""
    security = Mock()
    security.detect_threat = AsyncMock(return_value=False)
    security.add_rule = AsyncMock(return_value="rule_123")
    security.get_events = AsyncMock(return_value=[])
    security.analyze_transaction = AsyncMock(return_value={"risk": "low"})
    return security

@pytest.fixture
def sample_account_data() -> dict:
    """Sample XRPL account data for testing."""
    return {
        "account": "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
        "balance": "1000000000",
        "sequence": 12345,
        "reserve": "10000000",
        "flags": 0
    }

@pytest.fixture
def sample_order_data() -> dict:
    """Sample order data for testing."""
    return {
        "id": "order_123",
        "pair": "XRP/USD",
        "side": "buy",
        "type": "limit",
        "amount": "1000.00",
        "price": "0.50",
        "status": "open",
        "timestamp": 1640995200000
    }

@pytest.fixture
def sample_trade_data() -> dict:
    """Sample trade data for testing."""
    return {
        "id": "trade_123",
        "buy_order_id": "order_123",
        "sell_order_id": "order_124",
        "amount": "1000.00",
        "price": "0.50",
        "timestamp": 1640995200000
    }

@pytest.fixture
def sample_nft_data() -> dict:
    """Sample NFT data for testing."""
    return {
        "id": "nft_123",
        "name": "Test NFT",
        "description": "A test NFT",
        "image": "https://example.com/image.png",
        "owner": "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
        "price": "10.00",
        "for_sale": True,
        "metadata": {
            "attributes": [
                {"trait_type": "Color", "value": "Blue"}
            ]
        }
    }

@pytest.fixture
def sample_ai_agent_data() -> dict:
    """Sample AI agent data for testing."""
    return {
        "id": "agent_123",
        "name": "Test Trading Bot",
        "description": "A test AI trading bot",
        "type": "trading",
        "status": "active",
        "performance": {
            "win_rate": 75.5,
            "total_trades": 100,
            "profit_loss": "250.00"
        }
    }

@pytest.fixture
def sample_bridge_transaction_data() -> dict:
    """Sample bridge transaction data for testing."""
    return {
        "id": "bridge_123",
        "from_network": "XRPL",
        "to_network": "Ethereum",
        "amount": "1000.00",
        "asset": "XRP",
        "status": "completed",
        "timestamp": 1640995200000
    }

@pytest.fixture
def sample_security_event_data() -> dict:
    """Sample security event data for testing."""
    return {
        "id": "event_123",
        "type": "warning",
        "level": "medium",
        "message": "Unusual trading activity detected",
        "timestamp": 1640995200000,
        "resolved": False
    }

@pytest.fixture
def test_config() -> dict:
    """Test configuration."""
    return {
        "XRPL_NETWORK": "testnet",
        "XRPL_ACCOUNT": "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
        "XRPL_SECRET": "test_secret",
        "REDIS_URL": "redis://localhost:6379",
        "DATABASE_URL": "sqlite:///test.db",
        "AI_API_KEY": "test_api_key"
    }

@pytest.fixture
def mock_redis() -> Mock:
    """Mock Redis client for testing."""
    redis = Mock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    redis.exists = AsyncMock(return_value=False)
    redis.expire = AsyncMock(return_value=True)
    return redis

@pytest.fixture
def mock_database() -> Mock:
    """Mock database connection for testing."""
    db = Mock()
    db.execute = AsyncMock(return_value=Mock())
    db.fetch_one = AsyncMock(return_value=None)
    db.fetch_all = AsyncMock(return_value=[])
    db.commit = AsyncMock(return_value=None)
    db.rollback = AsyncMock(return_value=None)
    return db

@pytest.fixture
def mock_ai_client() -> Mock:
    """Mock AI client for testing."""
    client = Mock()
    client.analyze_market = AsyncMock(return_value={
        "sentiment": "bullish",
        "confidence": 0.85,
        "recommendations": ["buy"]
    })
    client.generate_trading_signal = AsyncMock(return_value={
        "action": "buy",
        "confidence": 0.75,
        "reasoning": "Strong momentum detected"
    })
    client.detect_anomaly = AsyncMock(return_value=False)
    return client

# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "requires_network: Tests requiring network access")
    config.addinivalue_line("markers", "requires_database: Tests requiring database")
    config.addinivalue_line("markers", "requires_redis: Tests requiring Redis")

# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add unit marker to tests in unit directories
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests in integration directories
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add e2e marker to tests in e2e directories
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        
        # Add slow marker to tests with "slow" in the name
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)

# Test reporting
def pytest_html_report_title(report):
    """Set the title of the HTML report."""
    report.title = "XRPL Ecosystem Test Report"

def pytest_html_results_summary(prefix, summary, postfix):
    """Customize the HTML report summary."""
    prefix.extend([
        "<p>XRPL Ecosystem Test Suite</p>",
        "<p>Testing comprehensive platform functionality</p>"
    ])
