# Cross-Chain Bridge Engine

A comprehensive cross-chain bridge solution for the XRPL DEX Platform that enables seamless asset transfers between XRPL and other blockchain networks.

## Features

- **Multi-Network Support**: XRPL, Ethereum, BSC, Polygon, Arbitrum, Optimism
- **Automated Processing**: Fully automated bridge transfers with confirmation tracking
- **Fee Calculation**: Dynamic fee calculation based on network and transfer amount
- **Transaction Tracking**: Real-time status updates and transaction history
- **Security**: Multi-layer security with confirmation requirements
- **Statistics**: Comprehensive bridge statistics and analytics

## Supported Networks

| Network | Type | Native Token | Min Confirmations | Fee Rate |
|---------|------|--------------|-------------------|----------|
| XRPL | Native | XRP | 1 | 0.000012 XRP |
| Ethereum | EVM | ETH | 12 | 0.001 ETH |
| BSC | EVM | BNB | 3 | 0.0005 BNB |
| Polygon | EVM | MATIC | 5 | 0.0001 MATIC |
| Arbitrum | EVM | ETH | 8 | 0.0008 ETH |
| Optimism | EVM | ETH | 8 | 0.0008 ETH |

## Bridge Process

1. **Initiation**: User initiates bridge transfer with source/target networks and amount
2. **Asset Locking**: Assets are locked on the source network
3. **Confirmation**: Wait for required confirmations on source network
4. **Asset Minting**: Assets are minted/released on target network
5. **Completion**: Transfer is marked as completed

## Usage

### Basic Bridge Transfer

```python
from cross_chain_bridge import CrossChainBridge, NetworkType
from decimal import Decimal

# Initialize bridge
config = {
    'xrpl_rpc_url': 'wss://xrplcluster.com',
    'eth_rpc_url': 'https://mainnet.infura.io/v3/your_key',
    'bsc_rpc_url': 'https://bsc-dataseed.binance.org/',
    'polygon_rpc_url': 'https://polygon-rpc.com/'
}

bridge = CrossChainBridge(config)

# Initiate bridge transfer
bridge_tx = await bridge.initiate_bridge_transfer(
    source_network=NetworkType.XRPL,
    target_network=NetworkType.ETHEREUM,
    source_address="rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH",
    target_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    amount=Decimal('1000'),
    token="XRP"
)
```

### Check Transaction Status

```python
# Get transaction status
status = await bridge.get_transaction_status(bridge_tx.id)
print(f"Status: {status.status.value}")
print(f"Confirmations: {status.confirmation_blocks}")
```

### Get Bridge Fees

```python
# Get fees for different amounts
fees = await bridge.get_bridge_fees(NetworkType.XRPL, NetworkType.ETHEREUM)
for amount, fee in fees.items():
    print(f"{amount} XRP: {fee} XRP fee")
```

### Bridge Statistics

```python
# Get bridge statistics
stats = await bridge.get_bridge_statistics()
print(f"Total Volume: ${stats['total_volume']:,.2f}")
print(f"Success Rate: {stats['success_rate']:.1f}%")
```

## Configuration

### Network Configuration

Each network requires specific configuration:

```python
NetworkConfig(
    name="Ethereum",
    type=NetworkType.ETHEREUM,
    rpc_url="https://mainnet.infura.io/v3/your_key",
    chain_id=1,
    native_token="ETH",
    gas_token="ETH",
    bridge_contract="0x...",
    min_confirmations=12,
    fee_rate=Decimal('0.001')
)
```

### Environment Variables

```env
XRPL_RPC_URL=wss://xrplcluster.com
ETH_RPC_URL=https://mainnet.infura.io/v3/your_key
BSC_RPC_URL=https://bsc-dataseed.binance.org/
POLYGON_RPC_URL=https://polygon-rpc.com/
ETH_BRIDGE_CONTRACT=0x...
BSC_BRIDGE_CONTRACT=0x...
POLYGON_BRIDGE_CONTRACT=0x...
```

## Security Features

- **Confirmation Requirements**: Each network has minimum confirmation requirements
- **Transaction Validation**: All transactions are validated before processing
- **Fee Protection**: Dynamic fee calculation prevents spam attacks
- **Status Tracking**: Complete transaction lifecycle tracking
- **Error Handling**: Comprehensive error handling and recovery

## API Endpoints

### REST API

- `POST /bridge/transfer` - Initiate bridge transfer
- `GET /bridge/status/{id}` - Get transaction status
- `GET /bridge/fees` - Get bridge fees
- `GET /bridge/statistics` - Get bridge statistics
- `POST /bridge/cancel/{id}` - Cancel pending transaction

### WebSocket API

- `bridge.status` - Real-time status updates
- `bridge.confirmation` - Confirmation notifications
- `bridge.completion` - Transfer completion notifications

## Monitoring and Analytics

The bridge engine provides comprehensive monitoring and analytics:

- **Transaction Volume**: Total volume processed
- **Success Rate**: Percentage of successful transfers
- **Network Performance**: Per-network statistics
- **Fee Analytics**: Fee collection and distribution
- **Error Tracking**: Failed transaction analysis

## Error Handling

The bridge engine handles various error scenarios:

- **Network Failures**: Automatic retry mechanisms
- **Insufficient Funds**: Clear error messages
- **Invalid Addresses**: Address validation
- **Timeout Handling**: Configurable timeouts
- **Recovery Procedures**: Automatic recovery from failures

## Development

### Prerequisites

- Python 3.8+
- asyncio support
- aiohttp for HTTP requests
- Decimal for precise calculations

### Installation

```bash
pip install -r requirements.txt
```

### Testing

```bash
python -m pytest tests/
```

### Running

```bash
python bridge_engine.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
