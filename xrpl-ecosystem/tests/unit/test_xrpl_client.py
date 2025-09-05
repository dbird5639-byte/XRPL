"""
Unit tests for XRPL Client
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from core.xrpl_client.client import XRPLClient
from core.xrpl_client.utils import drops_to_xrp, xrp_to_drops


class TestXRPLClient:
    """Test cases for XRPL Client"""

    @pytest.fixture
    def xrpl_client(self, mock_xrpl_client):
        """Create XRPL client instance for testing."""
        with patch('core.xrpl_client.client.Client') as mock_client_class:
            mock_client_class.return_value = mock_xrpl_client
            client = XRPLClient(
                network="testnet",
                account="rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
                secret="test_secret"
            )
            return client

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_connect(self, xrpl_client):
        """Test client connection."""
        result = await xrpl_client.connect()
        assert result is True
        xrpl_client._client.connect.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_disconnect(self, xrpl_client):
        """Test client disconnection."""
        result = await xrpl_client.disconnect()
        assert result is True
        xrpl_client._client.disconnect.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_account_info(self, xrpl_client, sample_account_data):
        """Test getting account information."""
        xrpl_client._client.get_account_info.return_value = sample_account_data
        
        result = await xrpl_client.get_account_info("rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH")
        
        assert result == sample_account_data
        xrpl_client._client.get_account_info.assert_called_once_with("rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_balances(self, xrpl_client):
        """Test getting account balances."""
        expected_balances = [
            {"currency": "XRP", "value": "1000.000000", "issuer": None}
        ]
        xrpl_client._client.get_balances.return_value = expected_balances
        
        result = await xrpl_client.get_balances("rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH")
        
        assert result == expected_balances
        xrpl_client._client.get_balances.assert_called_once_with("rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_send_payment(self, xrpl_client):
        """Test sending payment."""
        xrpl_client._client.send_payment.return_value = "tx_hash_123"
        
        result = await xrpl_client.send_payment(
            from_account="rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
            to_account="rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
            amount="100.00",
            currency="XRP"
        )
        
        assert result == "tx_hash_123"
        xrpl_client._client.send_payment.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_send_payment_with_memo(self, xrpl_client):
        """Test sending payment with memo."""
        xrpl_client._client.send_payment.return_value = "tx_hash_123"
        
        result = await xrpl_client.send_payment(
            from_account="rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
            to_account="rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
            amount="100.00",
            currency="XRP",
            memo="Test payment"
        )
        
        assert result == "tx_hash_123"
        xrpl_client._client.send_payment.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_transaction_history(self, xrpl_client):
        """Test getting transaction history."""
        expected_history = [
            {
                "hash": "tx_hash_123",
                "type": "Payment",
                "amount": "100.00",
                "fee": "0.000012",
                "date": "2024-01-15T10:30:00Z",
                "status": "success"
            }
        ]
        xrpl_client._client.get_transaction_history.return_value = expected_history
        
        result = await xrpl_client.get_transaction_history("rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH")
        
        assert result == expected_history
        xrpl_client._client.get_transaction_history.assert_called_once_with("rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_connection_error_handling(self, xrpl_client):
        """Test connection error handling."""
        xrpl_client._client.connect.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="Connection failed"):
            await xrpl_client.connect()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_invalid_account_handling(self, xrpl_client):
        """Test invalid account handling."""
        xrpl_client._client.get_account_info.side_effect = Exception("Invalid account")
        
        with pytest.raises(Exception, match="Invalid account"):
            await xrpl_client.get_account_info("invalid_account")

    @pytest.mark.unit
    def test_client_initialization(self):
        """Test client initialization."""
        with patch('core.xrpl_client.client.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            client = XRPLClient(
                network="testnet",
                account="rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
                secret="test_secret"
            )
            
            assert client.network == "testnet"
            assert client.account == "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH"
            assert client.secret == "test_secret"
            assert client._client == mock_client

    @pytest.mark.unit
    def test_network_configuration(self):
        """Test network configuration."""
        with patch('core.xrpl_client.client.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Test testnet configuration
            client = XRPLClient(network="testnet")
            assert client.network == "testnet"
            
            # Test mainnet configuration
            client = XRPLClient(network="mainnet")
            assert client.network == "mainnet"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, xrpl_client):
        """Test retry mechanism for failed requests."""
        # First call fails, second call succeeds
        xrpl_client._client.get_account_info.side_effect = [
            Exception("Network error"),
            {"account": "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH", "balance": "1000"}
        ]
        
        result = await xrpl_client.get_account_info("rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH")
        
        assert result["account"] == "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH"
        assert xrpl_client._client.get_account_info.call_count == 2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiting(self, xrpl_client):
        """Test rate limiting handling."""
        xrpl_client._client.get_account_info.side_effect = Exception("Rate limited")
        
        with pytest.raises(Exception, match="Rate limited"):
            await xrpl_client.get_account_info("rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, xrpl_client):
        """Test handling concurrent requests."""
        xrpl_client._client.get_account_info.return_value = {"account": "test"}
        
        # Make multiple concurrent requests
        tasks = [
            xrpl_client.get_account_info("account1"),
            xrpl_client.get_account_info("account2"),
            xrpl_client.get_account_info("account3")
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert all(result["account"] == "test" for result in results)
        assert xrpl_client._client.get_account_info.call_count == 3


class TestXRPLUtils:
    """Test cases for XRPL utility functions"""

    @pytest.mark.unit
    def test_drops_to_xrp(self):
        """Test converting drops to XRP."""
        assert drops_to_xrp("1000000") == "1.000000"
        assert drops_to_xrp("5000000") == "5.000000"
        assert drops_to_xrp("1234567") == "1.234567"
        assert drops_to_xrp("0") == "0.000000"

    @pytest.mark.unit
    def test_xrp_to_drops(self):
        """Test converting XRP to drops."""
        assert xrp_to_drops("1.000000") == "1000000"
        assert xrp_to_drops("5.000000") == "5000000"
        assert xrp_to_drops("1.234567") == "1234567"
        assert xrp_to_drops("0.000000") == "0"

    @pytest.mark.unit
    def test_drops_to_xrp_invalid_input(self):
        """Test drops_to_xrp with invalid input."""
        with pytest.raises(ValueError):
            drops_to_xrp("invalid")
        
        with pytest.raises(ValueError):
            drops_to_xrp("-1000000")

    @pytest.mark.unit
    def test_xrp_to_drops_invalid_input(self):
        """Test xrp_to_drops with invalid input."""
        with pytest.raises(ValueError):
            xrp_to_drops("invalid")
        
        with pytest.raises(ValueError):
            xrp_to_drops("-1.000000")

    @pytest.mark.unit
    def test_round_trip_conversion(self):
        """Test round-trip conversion between XRP and drops."""
        original_xrp = "1.234567"
        drops = xrp_to_drops(original_xrp)
        converted_xrp = drops_to_xrp(drops)
        assert converted_xrp == original_xrp

    @pytest.mark.unit
    def test_precision_handling(self):
        """Test precision handling in conversions."""
        # Test with maximum precision
        xrp = "999999999999.999999"
        drops = xrp_to_drops(xrp)
        converted_xrp = drops_to_xrp(drops)
        assert converted_xrp == xrp

    @pytest.mark.unit
    def test_edge_cases(self):
        """Test edge cases in conversions."""
        # Test very small amounts
        assert drops_to_xrp("1") == "0.000001"
        assert xrp_to_drops("0.000001") == "1"
        
        # Test very large amounts
        large_xrp = "1000000000.000000"
        large_drops = xrp_to_drops(large_xrp)
        assert large_drops == "1000000000000000"
