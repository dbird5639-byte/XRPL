# XRPL Ecosystem Frontend

A unified React-based frontend ecosystem for the XRPL platform, featuring multiple applications with shared components and utilities.

## 🏗️ Architecture

### Applications
- **Web Interface**: Main trading and DeFi platform
- **Xaman Wallet**: Mobile-first wallet application
- **AI IDE**: AI-powered development environment

### Shared Components
- **Components**: Reusable UI components (Button, Input, Modal, Table)
- **Types**: TypeScript type definitions
- **Constants**: Application constants and configuration
- **Utils**: Utility functions and helpers

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- npm or yarn
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd xrpl-ecosystem/frontend

# Install all dependencies
npm run install:all

# Start all applications in development mode
npm run dev
```

### Individual Applications

```bash
# Web Interface
npm run dev:web

# Xaman Wallet
npm run dev:wallet

# AI IDE
npm run dev:ide
```

## 📦 Project Structure

```
frontend/
├── shared/                 # Shared components and utilities
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── types/          # TypeScript definitions
│   │   ├── constants/      # Application constants
│   │   └── utils/          # Utility functions
│   └── package.json
├── web-interface/          # Main trading platform
├── xaman-wallet/           # Mobile wallet app
├── ai-ide/                 # AI development environment
└── package.json           # Root package configuration
```

## 🎨 Shared Components

### Button
```tsx
import { Button } from '@xrpl-ecosystem/shared';

<Button variant="primary" size="md" onClick={handleClick}>
  Click me
</Button>
```

### Input
```tsx
import { Input } from '@xrpl-ecosystem/shared';

<Input
  type="text"
  placeholder="Enter amount"
  value={amount}
  onChange={setAmount}
  error={error}
/>
```

### Modal
```tsx
import { Modal } from '@xrpl-ecosystem/shared';

<Modal isOpen={isOpen} onClose={onClose} title="Confirm Transaction">
  <p>Are you sure you want to proceed?</p>
</Modal>
```

### Table
```tsx
import { Table } from '@xrpl-ecosystem/shared';

<Table
  data={orders}
  columns={orderColumns}
  loading={loading}
  onRowClick={handleRowClick}
/>
```

## 🔧 Development

### Adding New Components

1. Create component in `shared/src/components/`
2. Export from `shared/src/components/index.ts`
3. Use in applications

### Adding New Utilities

1. Add utility function to `shared/src/utils/`
2. Export from `shared/src/utils/index.ts`
3. Import and use in applications

### Styling

All components use Tailwind CSS for styling. The shared components are designed to be:
- Responsive
- Accessible
- Themeable
- Consistent

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests for specific application
npm run test:web
npm run test:wallet
npm run test:ide
```

## 📱 Applications

### Web Interface
- **Purpose**: Main trading and DeFi platform
- **Features**: Trading, DeFi protocols, NFT marketplace, AI tools
- **Port**: 3000

### Xaman Wallet
- **Purpose**: Mobile-first wallet application
- **Features**: Wallet management, transactions, DeFi access
- **Port**: 3001

### AI IDE
- **Purpose**: AI-powered development environment
- **Features**: Code generation, AI agents, automation
- **Port**: 3002

## 🌐 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🆘 Support

- [Documentation](../../docs)
- [Issues](https://github.com/xrpl-ecosystem/frontend/issues)
- [Discord](https://discord.gg/xrpl-ecosystem)

---

**Built with ❤️ for the XRPL Ecosystem**
