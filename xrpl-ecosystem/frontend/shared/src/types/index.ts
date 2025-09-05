// XRPL Ecosystem Shared Types

export interface XRPLAccount {
  address: string;
  balance: string;
  sequence: number;
  reserve: string;
  flags: number;
}

export interface XRPLBalance {
  currency: string;
  value: string;
  issuer?: string;
}

export interface XRPLTransaction {
  hash: string;
  type: string;
  amount: string;
  fee: string;
  date: string;
  status: 'pending' | 'success' | 'failed';
  from: string;
  to: string;
}

export interface Order {
  id: string;
  type: 'buy' | 'sell';
  amount: string;
  price: string;
  total: string;
  status: 'open' | 'filled' | 'cancelled';
  timestamp: number;
}

export interface Trade {
  id: string;
  buyOrderId: string;
  sellOrderId: string;
  amount: string;
  price: string;
  timestamp: number;
}

export interface NFT {
  id: string;
  name: string;
  description: string;
  image: string;
  owner: string;
  price?: string;
  forSale: boolean;
  metadata: Record<string, any>;
}

export interface DeFiPosition {
  id: string;
  type: 'lending' | 'borrowing' | 'liquidity';
  asset: string;
  amount: string;
  apy: number;
  timestamp: number;
}

export interface AIAgent {
  id: string;
  name: string;
  description: string;
  type: 'trading' | 'analysis' | 'automation';
  status: 'active' | 'inactive' | 'training';
  performance: {
    winRate: number;
    totalTrades: number;
    profitLoss: string;
  };
}

export interface BridgeTransaction {
  id: string;
  fromNetwork: string;
  toNetwork: string;
  amount: string;
  asset: string;
  status: 'pending' | 'completed' | 'failed';
  timestamp: number;
}

export interface SecurityEvent {
  id: string;
  type: 'threat' | 'warning' | 'info';
  level: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: number;
  resolved: boolean;
}

export interface WalletConnection {
  address: string;
  network: string;
  connected: boolean;
  balance: string;
}

export interface NetworkConfig {
  name: string;
  chainId: number;
  rpcUrl: string;
  explorerUrl: string;
  nativeCurrency: {
    name: string;
    symbol: string;
    decimals: number;
  };
}

export interface ThemeConfig {
  mode: 'light' | 'dark';
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: string;
}

export interface UserPreferences {
  theme: ThemeConfig;
  language: string;
  notifications: {
    trades: boolean;
    security: boolean;
    updates: boolean;
  };
  trading: {
    defaultSlippage: number;
    autoApprove: boolean;
    confirmTransactions: boolean;
  };
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export interface ChartData {
  timestamp: number;
  value: number;
  label?: string;
}

export interface MarketData {
  symbol: string;
  price: number;
  change24h: number;
  volume24h: number;
  marketCap: number;
  high24h: number;
  low24h: number;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: number;
  read: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// Component Props Types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface ButtonProps extends BaseComponentProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
}

export interface InputProps extends BaseComponentProps {
  type?: 'text' | 'email' | 'password' | 'number';
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  disabled?: boolean;
}

export interface ModalProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export interface TableProps<T> extends BaseComponentProps {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  onRowClick?: (row: T) => void;
}

export interface TableColumn<T> {
  key: keyof T;
  title: string;
  render?: (value: any, row: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

// Hook Types
export interface UseXRPLReturn {
  account: XRPLAccount | null;
  balance: XRPLBalance[];
  connect: () => Promise<void>;
  disconnect: () => void;
  sendTransaction: (transaction: any) => Promise<string>;
  loading: boolean;
  error: string | null;
}

export interface UseTradingReturn {
  orders: Order[];
  trades: Trade[];
  placeOrder: (order: Omit<Order, 'id' | 'timestamp'>) => Promise<void>;
  cancelOrder: (orderId: string) => Promise<void>;
  loading: boolean;
  error: string | null;
}

export interface UseDeFiReturn {
  positions: DeFiPosition[];
  deposit: (asset: string, amount: string) => Promise<void>;
  withdraw: (asset: string, amount: string) => Promise<void>;
  borrow: (asset: string, amount: string) => Promise<void>;
  repay: (asset: string, amount: string) => Promise<void>;
  loading: boolean;
  error: string | null;
}

export interface UseNFTReturn {
  nfts: NFT[];
  createNFT: (metadata: any) => Promise<string>;
  listNFT: (nftId: string, price: string) => Promise<void>;
  buyNFT: (nftId: string) => Promise<void>;
  loading: boolean;
  error: string | null;
}

export interface UseAIReturn {
  agents: AIAgent[];
  createAgent: (config: any) => Promise<string>;
  updateAgent: (agentId: string, config: any) => Promise<void>;
  deleteAgent: (agentId: string) => Promise<void>;
  loading: boolean;
  error: string | null;
}

export interface UseBridgeReturn {
  transactions: BridgeTransaction[];
  bridge: (fromNetwork: string, toNetwork: string, amount: string, asset: string) => Promise<string>;
  loading: boolean;
  error: string | null;
}

export interface UseSecurityReturn {
  events: SecurityEvent[];
  addRule: (rule: any) => Promise<void>;
  removeRule: (ruleId: string) => Promise<void>;
  loading: boolean;
  error: string | null;
}
