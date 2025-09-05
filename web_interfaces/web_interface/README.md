# XRPL DEX Web Interface

A modern, responsive web interface for the XRPL DEX Platform built with React, TypeScript, and Tailwind CSS.

## Features

- **Trading Interface**: Advanced trading with order book, real-time charts, and order management
- **DeFi Integration**: Yield farming, liquidity pools, and lending protocols
- **NFT Marketplace**: Buy, sell, and create NFTs with energy-based mechanics
- **Portfolio Management**: Track investments with detailed analytics and performance metrics
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Real-time Updates**: Live market data and price updates
- **Security**: Multi-layer security with 2FA and API key management

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Charts**: Recharts
- **Icons**: Lucide React
- **Routing**: React Router DOM
- **HTTP Client**: Axios

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout component
│   ├── Sidebar.tsx     # Navigation sidebar
│   └── Header.tsx      # Top header bar
├── pages/              # Page components
│   ├── Home.tsx        # Dashboard home page
│   ├── Trading.tsx     # Trading interface
│   ├── DeFi.tsx        # DeFi protocols
│   ├── NFTs.tsx        # NFT marketplace
│   ├── Portfolio.tsx   # Portfolio management
│   └── Settings.tsx    # User settings
├── stores/             # State management
├── utils/              # Utility functions
├── types/              # TypeScript type definitions
├── App.tsx             # Main app component
├── main.tsx            # App entry point
└── index.css           # Global styles
```

## Features Overview

### Trading
- Real-time order book
- Advanced order types (market, limit, stop)
- Trading charts and indicators
- Portfolio tracking

### DeFi
- Yield farming pools
- Liquidity provision
- Lending and borrowing
- Staking rewards

### NFTs
- Marketplace browsing
- NFT creation and minting
- Energy-based NFT mechanics
- Collection management

### Portfolio
- Asset allocation charts
- Performance analytics
- Transaction history
- Risk management

## Configuration

The app can be configured through environment variables:

```env
VITE_API_BASE_URL=https://api.xrpl-dex.com
VITE_WS_URL=wss://ws.xrpl-dex.com
VITE_CHAIN_ID=1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
