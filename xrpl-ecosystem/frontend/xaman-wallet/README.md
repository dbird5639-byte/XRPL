# xAman Wallet xApp

A comprehensive XRPL wallet xApp built with React, TypeScript, and modern web technologies. This application provides a complete DeFi experience on the XRP Ledger with advanced features like yield farming, trading, NFT management, and more.

## 🚀 Features

### Core Wallet Features
- **Secure Wallet Management**: Create, import, and manage XRPL wallets
- **Multi-Network Support**: Testnet, Devnet, and Mainnet support
- **Real-time Balance Tracking**: Live balance updates and transaction monitoring
- **QR Code Generation**: Easy sharing of wallet addresses
- **Wallet Export/Import**: Secure backup and restore functionality

### DeFi Integration
- **Yield Farming**: Stake tokens in various liquidity pools
- **Flash Loans**: Execute arbitrage strategies with flash loans
- **Liquidity Provision**: Provide liquidity and earn rewards
- **Pool Management**: Create and manage custom pools
- **Risk Assessment**: Advanced risk scoring and management

### Trading Features
- **DEX Integration**: Trade directly on XRPL DEX
- **Order Management**: Place, modify, and cancel orders
- **Portfolio Analytics**: Comprehensive portfolio tracking
- **Trading Signals**: AI-powered trading recommendations
- **Risk Management**: Stop-loss and take-profit orders

### NFT Platform
- **NFT Minting**: Create and mint NFTs on XRPL
- **Marketplace**: Buy, sell, and trade NFTs
- **Collection Management**: Organize and manage NFT collections
- **Metadata Support**: Rich metadata and media support

### Security Features
- **Fort Knox Security**: Multi-layer security system
- **Threat Detection**: AI-powered threat analysis
- **Rate Limiting**: Protection against abuse
- **Secure Storage**: Encrypted local storage
- **Audit Logging**: Complete transaction history

## 🛠️ Technology Stack

- **Frontend**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS, Framer Motion
- **State Management**: Zustand with persistence
- **Data Fetching**: TanStack Query (React Query)
- **XRPL Integration**: @xrplf/xrpl, @xrplf/xrpl-hooks
- **Charts**: Recharts
- **Icons**: Lucide React
- **Notifications**: React Hot Toast

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd xaman_wallet_xapp
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Build for production**
   ```bash
   npm run build
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_XRPL_NETWORK=testnet
VITE_XRPL_MAINNET_URL=wss://xrplcluster.com
VITE_XRPL_TESTNET_URL=wss://s.altnet.rippletest.net:51233
VITE_XRPL_DEVNET_URL=wss://s.devnet.rippletest.net:51233
```

### Network Configuration

The app supports three XRPL networks:
- **Testnet**: For development and testing
- **Devnet**: For experimental features
- **Mainnet**: For production use

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout component
│   ├── Sidebar.tsx     # Navigation sidebar
│   ├── Header.tsx      # Top header
│   └── LoadingScreen.tsx
├── pages/              # Page components
│   ├── Home.tsx        # Dashboard
│   ├── Wallet.tsx      # Wallet management
│   ├── DeFi.tsx        # DeFi features
│   ├── Trading.tsx     # Trading interface
│   ├── NFTs.tsx        # NFT management
│   └── Settings.tsx    # App settings
├── stores/             # State management
│   ├── walletStore.ts  # Wallet state
│   └── xrplStore.ts    # XRPL connection state
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
├── types/              # TypeScript type definitions
└── main.tsx           # App entry point
```

## 🔐 Security

### Wallet Security
- **Local Storage**: All sensitive data is encrypted and stored locally
- **No Server Storage**: Private keys never leave the user's device
- **Secure Generation**: Cryptographically secure wallet generation
- **Backup Support**: Encrypted wallet export functionality

### Network Security
- **HTTPS Only**: All network requests use secure connections
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: Protection against abuse and spam
- **Error Handling**: Secure error messages without sensitive data

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Configure environment variables
3. Deploy automatically on push

### Netlify
1. Build the project: `npm run build`
2. Upload the `dist` folder to Netlify
3. Configure redirects for SPA routing

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 📱 Mobile Support

The xApp is fully responsive and works on:
- **Desktop**: Full feature set
- **Tablet**: Optimized layout
- **Mobile**: Touch-friendly interface
- **PWA**: Installable as a Progressive Web App

## 🔄 Integration

### XRPL Integration
- **Account Management**: Create, import, and manage accounts
- **Transaction Submission**: Send payments and other transactions
- **Real-time Updates**: WebSocket connections for live data
- **Multi-signature Support**: Advanced account security

### DeFi Protocols
- **AMM Integration**: Automated market maker support
- **Liquidity Pools**: Create and manage pools
- **Yield Farming**: Stake tokens and earn rewards
- **Flash Loans**: Execute complex DeFi strategies

## 🧪 Testing

```bash
# Run unit tests
npm run test

# Run integration tests
npm run test:integration

# Run e2e tests
npm run test:e2e

# Coverage report
npm run test:coverage
```

## 📊 Performance

- **Bundle Size**: Optimized for fast loading
- **Code Splitting**: Lazy loading for better performance
- **Caching**: Intelligent caching strategies
- **Compression**: Gzip compression for assets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.xaman-wallet.app](https://docs.xaman-wallet.app)
- **Discord**: [Join our community](https://discord.gg/xaman-wallet)
- **GitHub Issues**: [Report bugs](https://github.com/xaman-wallet/issues)
- **Email**: support@xaman-wallet.app

## 🙏 Acknowledgments

- **XRPL Foundation**: For the amazing ledger technology
- **xrpl.js Team**: For the excellent JavaScript library
- **React Team**: For the powerful frontend framework
- **Community**: For feedback and contributions

---

**Built with ❤️ for the XRPL community**

*This xApp represents the future of XRPL wallet applications, combining security, usability, and advanced DeFi features in a single, powerful solution.*
