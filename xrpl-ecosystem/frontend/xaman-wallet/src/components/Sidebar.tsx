import React from 'react'
import { NavLink } from 'react-router-dom'
import { 
  Home, 
  Wallet, 
  TrendingUp, 
  BarChart3, 
  Image, 
  Settings,
  Zap
} from 'lucide-react'
import { useWalletStore } from '../stores/walletStore'

const Sidebar: React.FC = () => {
  const { address, balance } = useWalletStore()
  
  const navigation = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Wallet', href: '/wallet', icon: Wallet },
    { name: 'DeFi', href: '/defi', icon: TrendingUp },
    { name: 'Trading', href: '/trading', icon: BarChart3 },
    { name: 'NFTs', href: '/nfts', icon: Image },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  return (
    <div className="w-64 bg-white shadow-medium border-r border-secondary-200 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-secondary-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-secondary-900">xAman</h1>
            <p className="text-xs text-secondary-500">Wallet xApp</p>
          </div>
        </div>
      </div>
      
      {/* Wallet Info */}
      <div className="p-4 border-b border-secondary-200">
        <div className="bg-secondary-50 rounded-lg p-3">
          <p className="text-xs text-secondary-500 mb-1">Wallet Address</p>
          <p className="text-sm font-mono text-secondary-900 truncate">
            {address ? `${address.slice(0, 8)}...${address.slice(-8)}` : 'Not connected'}
          </p>
          {balance && (
            <p className="text-xs text-success-600 mt-1">
              {parseFloat(balance).toFixed(2)} XRP
            </p>
          )}
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navigation.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.href}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 border border-primary-200'
                      : 'text-secondary-700 hover:bg-secondary-50 hover:text-secondary-900'
                  }`
                }
              >
                <item.icon className="w-5 h-5" />
                <span>{item.name}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      
      {/* Footer */}
      <div className="p-4 border-t border-secondary-200">
        <div className="text-xs text-secondary-500 text-center">
          <p>Powered by XRPL</p>
          <p className="mt-1">Version 1.0.0</p>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
