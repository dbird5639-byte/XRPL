# XRPL Ecosystem Smart Contracts

A comprehensive suite of smart contracts for the XRPL Ecosystem, including cross-chain DeFi protocols, AI-powered applications, NFT marketplaces, and governance systems.

## 🏗️ Architecture

### Core Contracts
- **XRPToken**: ERC-20 token representing XRP on EVM sidechains
- **XRPLBridge**: Cross-chain bridge for transferring assets between XRPL and EVM networks
- **DeFiProtocol**: Lending, borrowing, and yield farming protocols
- **NFTMarketplace**: Decentralized marketplace for NFT trading

### Application Contracts
- **AIAgentFactory**: Factory for creating and managing AI agents
- **AIAutomationEngine**: Automation engine for AI-powered workflows
- **AIDatasetMarketplace**: Marketplace for AI datasets and models
- **AICitizenRightsFramework**: Framework for AI citizen rights and governance
- **CleanEnergyTradingPlatform**: Platform for clean energy credit trading
- **GlobalCooperationDAO**: DAO for global cooperation and governance
- **PeaceProtocolInfrastructure**: Infrastructure for peace and cooperation protocols

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- npm or yarn
- Hardhat
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd xrpl-ecosystem/smart-contracts

# Install dependencies
npm install

# Copy environment file
cp env.example .env

# Edit .env with your configuration
```

### Configuration

Edit the `.env` file with your network configurations:

```bash
# XRPL EVM Sidechain
XRPL_EVM_RPC_URL=https://evm-sidechain.xrpl.org
XRPL_EVM_CHAIN_ID=1440001

# Private key for deployment
PRIVATE_KEY=your_private_key_here

# API keys for verification
ETHERSCAN_API_KEY=your_etherscan_api_key
```

### Compilation

```bash
# Compile contracts
npm run compile
```

### Testing

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run gas report
npm run gas-report
```

### Deployment

```bash
# Deploy to local network
npm run deploy:local

# Deploy to testnet
npm run deploy:testnet

# Deploy to mainnet
npm run deploy:mainnet

# Deploy to all networks
npm run deploy:all
```

### Verification

```bash
# Verify contracts on testnet
npm run verify:testnet

# Verify contracts on mainnet
npm run verify:mainnet
```

## 📋 Contract Details

### XRPToken
- **Standard**: ERC-20
- **Features**: Mintable, burnable, pausable
- **Use Cases**: Cross-chain XRP representation, DeFi collateral

### XRPLBridge
- **Features**: Cross-chain asset transfers, multi-signature security
- **Networks**: XRPL ↔ EVM sidechains
- **Security**: Time-locked transactions, multi-sig validation

### DeFiProtocol
- **Features**: Lending, borrowing, yield farming, liquidity mining
- **Collateral**: XRP and other supported tokens
- **Interest**: Dynamic interest rates based on utilization

### NFTMarketplace
- **Features**: NFT creation, trading, auctions, royalties
- **Standards**: ERC-721, ERC-1155
- **Fees**: Configurable marketplace fees

### AI Framework
- **AIAgentFactory**: Create and manage AI agents
- **AIAutomationEngine**: Automate workflows with AI
- **AIDatasetMarketplace**: Trade AI datasets and models

## 🔧 Development

### Project Structure

```
smart-contracts/
├── core/                    # Core contracts
│   ├── XRPToken.sol
│   ├── XRPLBridge.sol
│   ├── DeFiProtocol.sol
│   └── NFTMarketplace.sol
├── applications/            # Application contracts
│   └── ai-framework/
│       ├── AIAgentFactory.sol
│       ├── AIAutomationEngine.sol
│       └── AIDatasetMarketplace.sol
├── deployment/             # Deployment artifacts
├── test/                   # Test files
├── scripts/                # Deployment scripts
├── hardhat.config.js       # Hardhat configuration
└── package.json           # Dependencies
```

### Adding New Contracts

1. Create contract file in appropriate directory
2. Add tests in `test/` directory
3. Update deployment script
4. Add to package.json contracts list
5. Update documentation

### Testing Guidelines

- Write comprehensive unit tests
- Include integration tests
- Test edge cases and error conditions
- Maintain high test coverage (>90%)
- Use fixtures for test setup

### Security Considerations

- Use OpenZeppelin contracts for security
- Implement proper access controls
- Add reentrancy guards where needed
- Use safe math operations
- Implement emergency pause functionality

## 🌐 Network Support

### Supported Networks

| Network | Chain ID | Status | Bridge Support |
|---------|----------|--------|----------------|
| XRPL EVM | 1440001 | ✅ Mainnet | ✅ |
| XRPL EVM Testnet | 1440002 | ✅ Testnet | ✅ |
| Ethereum | 1 | ✅ Mainnet | ✅ |
| Ethereum Sepolia | 11155111 | ✅ Testnet | ✅ |
| BSC | 56 | ✅ Mainnet | ✅ |
| BSC Testnet | 97 | ✅ Testnet | ✅ |
| Polygon | 137 | ✅ Mainnet | ✅ |
| Polygon Mumbai | 80001 | ✅ Testnet | ✅ |
| Arbitrum | 42161 | ✅ Mainnet | ✅ |
| Arbitrum Goerli | 421613 | ✅ Testnet | ✅ |
| Optimism | 10 | ✅ Mainnet | ✅ |
| Optimism Goerli | 420 | ✅ Testnet | ✅ |

## 🔒 Security

### Audit Status
- [ ] Internal audit completed
- [ ] External audit scheduled
- [ ] Bug bounty program active

### Security Features
- Multi-signature wallets for admin functions
- Time-locked upgrades
- Emergency pause functionality
- Reentrancy protection
- Access control mechanisms

### Reporting Security Issues

If you discover a security vulnerability, please report it to:
- Email: security@xrpl-ecosystem.org
- Discord: #security channel
- GitHub: Private security advisory

## 📊 Gas Optimization

### Optimization Techniques
- Use `uint256` for storage variables
- Pack structs efficiently
- Use events instead of storage for logs
- Implement batch operations
- Use libraries for common functions

### Gas Usage Estimates

| Contract | Deployment | Key Function |
|----------|------------|--------------|
| XRPToken | ~800k gas | Transfer: ~21k gas |
| XRPLBridge | ~1.2M gas | Lock: ~100k gas |
| DeFiProtocol | ~1.5M gas | Deposit: ~80k gas |
| NFTMarketplace | ~1M gas | Create Listing: ~60k gas |

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run test suite
6. Submit pull request

### Code Standards

- Follow Solidity style guide
- Use meaningful variable names
- Add comprehensive comments
- Write clear commit messages
- Update documentation

### Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add changelog entry
4. Request review from maintainers
5. Address feedback
6. Merge after approval

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## 🆘 Support

### Documentation
- [API Documentation](./docs/API.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Integration Guide](./docs/INTEGRATION.md)

### Community
- [Discord](https://discord.gg/xrpl-ecosystem)
- [Telegram](https://t.me/xrpl_ecosystem)
- [Twitter](https://twitter.com/xrpl_ecosystem)

### Issues
- [GitHub Issues](https://github.com/xrpl-ecosystem/smart-contracts/issues)
- [Bug Reports](https://github.com/xrpl-ecosystem/smart-contracts/issues/new?template=bug_report.md)
- [Feature Requests](https://github.com/xrpl-ecosystem/smart-contracts/issues/new?template=feature_request.md)

---

**Built with ❤️ for the XRPL Ecosystem**
