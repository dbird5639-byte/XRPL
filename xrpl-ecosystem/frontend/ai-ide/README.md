# XRP AI IDE Demo

A decentralized, AI-powered Integrated Development Environment (IDE) for the XRP Ledger, combining the intelligence of Cursor with the accessibility of Remix's web-based interface.

## 🚀 Features

- **AI-Powered Code Generation**: Generate XRP Ledger smart contracts using natural language
- **Web-Based IDE**: Access from any device with a modern browser
- **XRP Ledger Integration**: Direct deployment to mainnet, testnet, or devnet
- **Smart Contract Templates**: Pre-built templates for common use cases
- **Real-time Collaboration**: Work with team members in real-time
- **Advanced Code Editor**: Monaco Editor with XRP Ledger syntax highlighting
- **AI Code Assistant**: Get explanations, suggestions, and error detection

## 🛠️ Tech Stack

- **Frontend**: React 18 + TypeScript
- **Code Editor**: Monaco Editor
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **AI Integration**: OpenAI API / Anthropic Claude
- **Blockchain**: XRP Ledger (xrpl.js)
- **Storage**: IPFS (decentralized)
- **Real-time**: WebSocket + Socket.io

## 📋 Prerequisites

- Node.js 18+ and npm
- XRP Ledger testnet account
- OpenAI API key (or alternative AI provider)
- Basic knowledge of React and blockchain development

## 🚀 Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd xrp-ai-ide-demo

# Install dependencies
npm install
```

### 2. Environment Setup

```bash
# Create environment file
cp .env.example .env

# Add your configuration
REACT_APP_OPENAI_API_KEY=your_openai_api_key
REACT_APP_XRP_NETWORK=testnet
REACT_APP_XRP_TESTNET_URL=wss://s.altnet.rippletest.net:51233
```

### 3. Start Development Server

```bash
npm start
```

The application will open at `http://localhost:3000`

## 🏗️ Project Structure

```
src/
├── components/          # React components
│   ├── Editor/         # Code editor components
│   ├── FileExplorer/   # File management
│   ├── Terminal/       # Command line interface
│   ├── ContractDeployer/ # Smart contract deployment
│   ├── AIAssistant/    # AI-powered assistance
│   └── Layout/         # Main layout components
├── services/           # Business logic services
│   ├── ai/            # AI service integration
│   ├── xrp/           # XRP Ledger integration
│   ├── storage/       # File storage (IPFS)
│   └── compilation/   # Smart contract compilation
├── stores/            # State management (Zustand)
├── hooks/             # Custom React hooks
├── types/             # TypeScript type definitions
└── utils/             # Utility functions
```

## 🔧 Configuration

### AI Service

The IDE supports multiple AI providers:

- **OpenAI GPT-4**: Default provider with excellent code generation
- **Anthropic Claude**: Alternative for code analysis and explanations
- **Local Models**: Self-hosted AI models for privacy

### XRP Ledger Networks

- **Mainnet**: Production XRP Ledger
- **Testnet**: Public test network
- **Devnet**: Development and testing network

### Smart Contract Languages

- **XRP Ledger Hooks**: Native smart contract language
- **TypeScript**: For tooling and utilities
- **JavaScript**: For extensions and plugins

## 📚 Smart Contract Templates

### Basic Token Contract

```typescript
hook my_token {
    const TOKEN_NAME = "MyToken";
    const TOKEN_SYMBOL = "MTK";
    const DECIMALS = 6;
    
    // Token transfer logic
    const transfer_amount = hook_param(0);
    if (transfer_amount <= 0) {
        return rollback(1, "Invalid amount");
    }
    
    return accept("Transfer successful", 0);
}
```

### DeFi Protocol Template

```typescript
hook defi_protocol {
    // Automated Market Maker logic
    const input_amount = hook_param(0);
    const output_amount = calculate_output(input_amount);
    
    if (output_amount <= 0) {
        return rollback(2, "Insufficient liquidity");
    }
    
    return accept("Swap successful", 0);
}
```

## 🚀 Deployment

### Development

```bash
npm start
```

### Production Build

```bash
npm run build
```

### Deploy to IPFS

```bash
# Install IPFS CLI
npm install -g ipfs

# Add build folder to IPFS
ipfs add -r build/

# Pin the content
ipfs pin add <hash>
```

### Deploy to Traditional Hosting

- **Vercel**: `vercel --prod`
- **Netlify**: `netlify deploy --prod`
- **AWS S3**: Use AWS CLI or CDK
- **GitHub Pages**: `npm run deploy`

## 🔐 Security Features

- **Wallet Integration**: Secure key management
- **Multi-signature**: Enhanced security for deployments
- **Code Auditing**: AI-powered security analysis
- **Access Control**: Role-based permissions
- **Encryption**: End-to-end encryption for sensitive data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📖 Documentation

- [XRP Ledger Developer Guide](https://xrpl.org/docs/)
- [Hooks Documentation](https://xrpl.org/docs/hooks/)
- [xrpl.js API Reference](https://js.xrpl.org/)
- [Monaco Editor Documentation](https://microsoft.github.io/monaco-editor/)

## 🐛 Troubleshooting

### Common Issues

1. **AI Service Not Working**
   - Check API key configuration
   - Verify API quota and limits
   - Check network connectivity

2. **XRP Ledger Connection Issues**
   - Verify network URL configuration
   - Check account credentials
   - Ensure sufficient XRP balance

3. **Build Errors**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify TypeScript configuration

### Getting Help

- Create an issue on GitHub
- Join our Discord community
- Check the troubleshooting guide

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- XRP Ledger community for blockchain infrastructure
- Monaco Editor team for the excellent code editor
- OpenAI/Anthropic for AI capabilities
- React and TypeScript communities

## 🔮 Roadmap

### Phase 1 (Current)
- [x] Basic IDE functionality
- [x] AI code generation
- [x] XRP Ledger integration
- [x] Smart contract deployment

### Phase 2 (Next 3 months)
- [ ] Advanced AI features
- [ ] Collaboration tools
- [ ] Plugin system
- [ ] Mobile optimization

### Phase 3 (Next 6 months)
- [ ] Multi-chain support
- [ ] Advanced analytics
- [ ] Enterprise features
- [ ] Community marketplace

---

**Built with ❤️ for the XRP Ledger community**

For questions and support, please open an issue or join our community channels.
