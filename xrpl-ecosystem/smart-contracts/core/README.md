# XRPL EVM Sidechain

A comprehensive EVM sidechain integration for the XRP Ledger, enabling smart contract functionality and seamless asset bridging between XRPL and Ethereum-compatible networks.

## 🚀 Features

### Core Bridge Functionality
- **Bidirectional Asset Transfer**: Move XRP and other assets between XRPL and EVM sidechain
- **Validator Network**: Decentralized validation system for secure cross-chain transactions
- **Real-time Monitoring**: Live transaction tracking and status updates
- **Multi-signature Support**: Enhanced security through validator consensus

### DeFi Protocol
- **Automated Market Maker (AMM)**: Create and manage liquidity pools
- **Yield Farming**: Stake tokens and earn rewards
- **Flash Loans**: Execute complex DeFi strategies
- **Liquidity Mining**: Earn rewards for providing liquidity

### Smart Contract Support
- **EVM Compatibility**: Deploy and interact with Ethereum smart contracts
- **Gas Optimization**: Efficient transaction processing
- **Developer Tools**: Full Hardhat and Remix support
- **Standard Interfaces**: ERC-20, ERC-721, ERC-1155 compatibility

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   XRPL Mainnet  │    │  EVM Sidechain  │    │  Validator      │
│                 │    │                 │    │  Network        │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │   Users   │  │◄──►│  │  Bridge   │  │◄──►│  │ Validators │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │  Assets   │  │    │  │ DeFi      │  │    │  │ Consensus │  │
│  └───────────┘  │    │  │ Protocol  │  │    │  └───────────┘  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📦 Installation

### Prerequisites
- Node.js 18+
- Hardhat
- XRPL account with testnet access
- Ethereum development environment

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd evm_sidechain
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Compile contracts**
   ```bash
   npm run compile
   ```

5. **Deploy contracts**
   ```bash
   npm run deploy
   ```

6. **Start the sidechain**
   ```bash
   npm run dev
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `XRPL_NETWORK` | XRPL network (mainnet/testnet/devnet) | testnet |
| `XRPL_SERVER_URL` | XRPL WebSocket URL | wss://s.altnet.rippletest.net:51233 |
| `VALIDATOR_SEED` | Validator wallet seed | - |
| `EVM_RPC_URL` | EVM RPC endpoint | http://localhost:8545 |
| `EVM_CHAIN_ID` | EVM chain ID | 1337 |
| `VALIDATOR_PRIVATE_KEY` | Validator private key | - |
| `PORT` | API server port | 3000 |

### Contract Configuration

After deployment, update your `.env` file with the deployed contract addresses:

```env
BRIDGE_CONTRACT_ADDRESS=0x...
XRP_TOKEN_ADDRESS=0x...
DEFI_CONTRACT_ADDRESS=0x...
```

## 🚀 Usage

### Bridge Operations

#### Deposit XRP to Sidechain
```bash
curl -X POST http://localhost:3000/api/bridge/deposit \
  -H "Content-Type: application/json" \
  -d '{
    "userAddress": "0x...",
    "amount": "100",
    "xrplAddress": "rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH"
  }'
```

#### Withdraw XRP from Sidechain
```bash
curl -X POST http://localhost:3000/api/bridge/withdraw \
  -H "Content-Type: application/json" \
  -d '{
    "userAddress": "0x...",
    "amount": "100",
    "xrplTxHash": "A1B2C3D4E5F6..."
  }'
```

### DeFi Operations

#### Create Liquidity Pool
```bash
curl -X POST http://localhost:3000/api/defi/pools \
  -H "Content-Type: application/json" \
  -d '{
    "tokenA": "0x...",
    "tokenB": "0x...",
    "initialAmountA": "1000",
    "initialAmountB": "1000",
    "feeRate": 30
  }'
```

#### Add Liquidity
```bash
curl -X POST http://localhost:3000/api/defi/pools/0/liquidity \
  -H "Content-Type: application/json" \
  -d '{
    "amountA": "100",
    "amountB": "100"
  }'
```

#### Swap Tokens
```bash
curl -X POST http://localhost:3000/api/defi/pools/0/swap \
  -H "Content-Type: application/json" \
  -d '{
    "tokenIn": "0x...",
    "amountIn": "50",
    "minAmountOut": "45"
  }'
```

## 🔐 Security

### Validator Network
- **Multi-signature Validation**: Transactions require multiple validator signatures
- **Threshold Configuration**: Configurable consensus requirements
- **Slashing Conditions**: Validators can be penalized for malicious behavior
- **Rotation System**: Regular validator rotation for security

### Smart Contract Security
- **OpenZeppelin Standards**: Using battle-tested security libraries
- **Reentrancy Protection**: Protection against reentrancy attacks
- **Access Control**: Role-based access control for sensitive functions
- **Pause Functionality**: Emergency pause mechanisms

### Bridge Security
- **Transaction Validation**: Comprehensive transaction verification
- **Double-spend Prevention**: Protection against double-spending attacks
- **Rate Limiting**: Protection against spam and abuse
- **Audit Logging**: Complete transaction audit trail

## 🧪 Testing

### Unit Tests
```bash
npm run test
```

### Integration Tests
```bash
npm run test:integration
```

### End-to-End Tests
```bash
npm run test:e2e
```

### Coverage Report
```bash
npm run test:coverage
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:3000/health
```

### Bridge Statistics
```bash
curl http://localhost:3000/api/bridge/stats
```

### Validator Status
```bash
curl http://localhost:3000/api/validator/status
```

## 🔄 Development

### Local Development Setup

1. **Start local EVM node**
   ```bash
   npx hardhat node
   ```

2. **Deploy contracts to local network**
   ```bash
   npx hardhat run scripts/deploy.ts --network localhost
   ```

3. **Start the sidechain service**
   ```bash
   npm run dev
   ```

### Smart Contract Development

1. **Create new contract**
   ```bash
   npx hardhat new-contract ContractName
   ```

2. **Compile contracts**
   ```bash
   npx hardhat compile
   ```

3. **Run tests**
   ```bash
   npx hardhat test
   ```

4. **Deploy to network**
   ```bash
   npx hardhat run scripts/deploy.ts --network <network>
   ```

## 🚀 Deployment

### Production Deployment

1. **Configure production environment**
   ```bash
   cp env.example .env.production
   # Update with production values
   ```

2. **Deploy contracts**
   ```bash
   npx hardhat run scripts/deploy.ts --network production
   ```

3. **Start production service**
   ```bash
   NODE_ENV=production npm start
   ```

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 📚 API Documentation

### Bridge API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/bridge/deposit` | POST | Deposit XRP to sidechain |
| `/api/bridge/withdraw` | POST | Withdraw XRP from sidechain |
| `/api/bridge/balance/:address` | GET | Get user balance |
| `/api/bridge/transaction/:txHash` | GET | Get transaction details |
| `/api/bridge/stats` | GET | Get bridge statistics |

### DeFi API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/defi/pools` | GET/POST | List/Create pools |
| `/api/defi/pools/:id/liquidity` | POST | Add liquidity |
| `/api/defi/pools/:id/swap` | POST | Swap tokens |
| `/api/defi/pools/:id/stake` | POST | Stake tokens |
| `/api/defi/pools/:id/quote` | GET | Get swap quote |

### Validator API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/validator/status` | GET | Get validator status |
| `/api/validator/stats` | GET | Get validator statistics |
| `/api/validator/transactions/pending` | GET | Get pending transactions |
| `/api/validator/config` | GET/PUT | Get/Update configuration |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.xrpl-sidechain.com](https://docs.xrpl-sidechain.com)
- **Discord**: [Join our community](https://discord.gg/xrpl-sidechain)
- **GitHub Issues**: [Report bugs](https://github.com/xrpl-sidechain/issues)
- **Email**: support@xrpl-sidechain.com

## 🙏 Acknowledgments

- **XRPL Foundation**: For the amazing ledger technology
- **Ethereum Foundation**: For EVM and smart contract standards
- **OpenZeppelin**: For security libraries and best practices
- **Hardhat Team**: For the excellent development framework

---

**Built with ❤️ for the XRPL and Ethereum communities**

*This sidechain represents the future of cross-chain interoperability, combining the speed and efficiency of XRPL with the flexibility and programmability of Ethereum smart contracts.*
