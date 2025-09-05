// XRPL Ecosystem Shared Constants

export const NETWORKS = {
  XRPL_MAINNET: {
    name: 'XRPL Mainnet',
    chainId: 1440001,
    rpcUrl: 'https://evm-sidechain.xrpl.org',
    explorerUrl: 'https://evm-sidechain.xrpl.org/explorer',
    nativeCurrency: {
      name: 'XRP',
      symbol: 'XRP',
      decimals: 18,
    },
  },
  XRPL_TESTNET: {
    name: 'XRPL Testnet',
    chainId: 1440002,
    rpcUrl: 'https://evm-sidechain-testnet.xrpl.org',
    explorerUrl: 'https://evm-sidechain-testnet.xrpl.org/explorer',
    nativeCurrency: {
      name: 'XRP',
      symbol: 'XRP',
      decimals: 18,
    },
  },
  ETHEREUM: {
    name: 'Ethereum',
    chainId: 1,
    rpcUrl: 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID',
    explorerUrl: 'https://etherscan.io',
    nativeCurrency: {
      name: 'Ether',
      symbol: 'ETH',
      decimals: 18,
    },
  },
  BSC: {
    name: 'BSC',
    chainId: 56,
    rpcUrl: 'https://bsc-dataseed.binance.org',
    explorerUrl: 'https://bscscan.com',
    nativeCurrency: {
      name: 'BNB',
      symbol: 'BNB',
      decimals: 18,
    },
  },
  POLYGON: {
    name: 'Polygon',
    chainId: 137,
    rpcUrl: 'https://polygon-rpc.com',
    explorerUrl: 'https://polygonscan.com',
    nativeCurrency: {
      name: 'MATIC',
      symbol: 'MATIC',
      decimals: 18,
    },
  },
  ARBITRUM: {
    name: 'Arbitrum',
    chainId: 42161,
    rpcUrl: 'https://arb1.arbitrum.io/rpc',
    explorerUrl: 'https://arbiscan.io',
    nativeCurrency: {
      name: 'Ether',
      symbol: 'ETH',
      decimals: 18,
    },
  },
  OPTIMISM: {
    name: 'Optimism',
    chainId: 10,
    rpcUrl: 'https://mainnet.optimism.io',
    explorerUrl: 'https://optimistic.etherscan.io',
    nativeCurrency: {
      name: 'Ether',
      symbol: 'ETH',
      decimals: 18,
    },
  },
} as const;

export const CONTRACT_ADDRESSES = {
  XRPL_MAINNET: {
    XRP_TOKEN: '0x...',
    XRPL_BRIDGE: '0x...',
    DEFI_PROTOCOL: '0x...',
    NFT_MARKETPLACE: '0x...',
    AI_AGENT_FACTORY: '0x...',
    AI_AUTOMATION_ENGINE: '0x...',
  },
  XRPL_TESTNET: {
    XRP_TOKEN: '0x...',
    XRPL_BRIDGE: '0x...',
    DEFI_PROTOCOL: '0x...',
    NFT_MARKETPLACE: '0x...',
    AI_AGENT_FACTORY: '0x...',
    AI_AUTOMATION_ENGINE: '0x...',
  },
} as const;

export const API_ENDPOINTS = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:3001',
  XRPL: '/api/xrpl',
  TRADING: '/api/trading',
  DEFI: '/api/defi',
  NFT: '/api/nft',
  AI: '/api/ai',
  BRIDGE: '/api/bridge',
  SECURITY: '/api/security',
} as const;

export const ROUTES = {
  HOME: '/',
  TRADING: '/trading',
  DEFI: '/defi',
  NFT: '/nft',
  AI: '/ai',
  BRIDGE: '/bridge',
  WALLET: '/wallet',
  SETTINGS: '/settings',
  PORTFOLIO: '/portfolio',
} as const;

export const THEMES = {
  LIGHT: {
    mode: 'light' as const,
    primary: '#1E40AF',
    secondary: '#64748B',
    accent: '#F59E0B',
    background: '#FFFFFF',
    surface: '#F8FAFC',
    text: '#1E293B',
  },
  DARK: {
    mode: 'dark' as const,
    primary: '#3B82F6',
    secondary: '#94A3B8',
    accent: '#F59E0B',
    background: '#0F172A',
    surface: '#1E293B',
    text: '#F1F5F9',
  },
} as const;

export const TRADING_PAIRS = [
  'XRP/USD',
  'XRP/BTC',
  'XRP/ETH',
  'BTC/USD',
  'ETH/USD',
  'BNB/USD',
  'MATIC/USD',
] as const;

export const ORDER_TYPES = {
  MARKET: 'market',
  LIMIT: 'limit',
  STOP: 'stop',
  STOP_LIMIT: 'stop_limit',
} as const;

export const ORDER_SIDES = {
  BUY: 'buy',
  SELL: 'sell',
} as const;

export const ORDER_STATUS = {
  OPEN: 'open',
  FILLED: 'filled',
  CANCELLED: 'cancelled',
  PARTIALLY_FILLED: 'partially_filled',
} as const;

export const TRANSACTION_TYPES = {
  PAYMENT: 'Payment',
  OFFER_CREATE: 'OfferCreate',
  OFFER_CANCEL: 'OfferCancel',
  TRUST_SET: 'TrustSet',
  ACCOUNT_SET: 'AccountSet',
} as const;

export const NFT_STANDARDS = {
  ERC721: 'ERC721',
  ERC1155: 'ERC1155',
} as const;

export const AI_AGENT_TYPES = {
  TRADING: 'trading',
  ANALYSIS: 'analysis',
  AUTOMATION: 'automation',
  PREDICTION: 'prediction',
} as const;

export const SECURITY_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
} as const;

export const SECURITY_EVENT_TYPES = {
  THREAT: 'threat',
  WARNING: 'warning',
  INFO: 'info',
} as const;

export const NOTIFICATION_TYPES = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error',
} as const;

export const CHART_TYPES = {
  LINE: 'line',
  CANDLESTICK: 'candlestick',
  BAR: 'bar',
  AREA: 'area',
} as const;

export const TIME_INTERVALS = {
  '1m': '1m',
  '5m': '5m',
  '15m': '15m',
  '1h': '1h',
  '4h': '4h',
  '1d': '1d',
  '1w': '1w',
  '1M': '1M',
} as const;

export const CURRENCIES = {
  XRP: 'XRP',
  USD: 'USD',
  BTC: 'BTC',
  ETH: 'ETH',
  BNB: 'BNB',
  MATIC: 'MATIC',
} as const;

export const LANGUAGES = {
  EN: 'en',
  ES: 'es',
  FR: 'fr',
  DE: 'de',
  ZH: 'zh',
  JA: 'ja',
  KO: 'ko',
} as const;

export const STORAGE_KEYS = {
  WALLET_CONNECTION: 'xrpl_wallet_connection',
  USER_PREFERENCES: 'xrpl_user_preferences',
  THEME: 'xrpl_theme',
  LANGUAGE: 'xrpl_language',
  NOTIFICATIONS: 'xrpl_notifications',
  TRADING_SETTINGS: 'xrpl_trading_settings',
} as const;

export const ERROR_MESSAGES = {
  WALLET_NOT_CONNECTED: 'Wallet not connected',
  INSUFFICIENT_BALANCE: 'Insufficient balance',
  TRANSACTION_FAILED: 'Transaction failed',
  NETWORK_ERROR: 'Network error',
  INVALID_ADDRESS: 'Invalid address',
  INVALID_AMOUNT: 'Invalid amount',
  ORDER_NOT_FOUND: 'Order not found',
  NFT_NOT_FOUND: 'NFT not found',
  AGENT_NOT_FOUND: 'AI Agent not found',
  BRIDGE_TRANSACTION_FAILED: 'Bridge transaction failed',
  SECURITY_THREAT_DETECTED: 'Security threat detected',
} as const;

export const SUCCESS_MESSAGES = {
  WALLET_CONNECTED: 'Wallet connected successfully',
  TRANSACTION_SUCCESSFUL: 'Transaction successful',
  ORDER_PLACED: 'Order placed successfully',
  ORDER_CANCELLED: 'Order cancelled successfully',
  NFT_CREATED: 'NFT created successfully',
  NFT_LISTED: 'NFT listed successfully',
  NFT_PURCHASED: 'NFT purchased successfully',
  AGENT_CREATED: 'AI Agent created successfully',
  AGENT_UPDATED: 'AI Agent updated successfully',
  AGENT_DELETED: 'AI Agent deleted successfully',
  BRIDGE_TRANSACTION_INITIATED: 'Bridge transaction initiated',
  SECURITY_RULE_ADDED: 'Security rule added successfully',
} as const;

export const VALIDATION_RULES = {
  ADDRESS: /^[a-zA-Z0-9]{25,34}$/,
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  AMOUNT: /^\d+(\.\d+)?$/,
  PRICE: /^\d+(\.\d+)?$/,
} as const;

export const DEFAULT_VALUES = {
  SLIPPAGE_TOLERANCE: 0.5,
  GAS_LIMIT: 21000,
  GAS_PRICE: 20,
  CONFIRMATION_BLOCKS: 1,
  REFRESH_INTERVAL: 5000,
  CHART_HEIGHT: 400,
  TABLE_PAGE_SIZE: 20,
  MAX_RETRIES: 3,
  TIMEOUT: 30000,
} as const;

export const FEATURE_FLAGS = {
  ENABLE_AI_TRADING: true,
  ENABLE_NFT_MARKETPLACE: true,
  ENABLE_CROSS_CHAIN_BRIDGE: true,
  ENABLE_DEFI_PROTOCOLS: true,
  ENABLE_SECURITY_MONITORING: true,
  ENABLE_ADVANCED_CHARTING: true,
  ENABLE_SOCIAL_TRADING: false,
  ENABLE_MOBILE_APP: false,
} as const;
