import React from 'react'
import { Bell, Search, User, LogOut } from 'lucide-react'
import { useWalletStore } from '../stores/walletStore'
import { useXRPLStore } from '../stores/xrplStore'

const Header: React.FC = () => {
  const { address, disconnect } = useWalletStore()
  const { network, ledgerIndex, isConnected } = useXRPLStore()
  
  const handleDisconnect = () => {
    disconnect()
  }

  return (
    <header className="bg-white border-b border-secondary-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary-400" />
            <input
              type="text"
              placeholder="Search transactions, addresses..."
              className="input pl-10 w-full"
            />
          </div>
        </div>
        
        {/* Network Status */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-success-500' : 'bg-error-500'
            }`} />
            <span className="text-sm text-secondary-600 capitalize">{network}</span>
            {ledgerIndex && (
              <span className="text-xs text-secondary-500">
                #{ledgerIndex.toLocaleString()}
              </span>
            )}
          </div>
          
          {/* Notifications */}
          <button className="p-2 text-secondary-400 hover:text-secondary-600 transition-colors">
            <Bell className="w-5 h-5" />
          </button>
          
          {/* User Menu */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <p className="text-sm font-medium text-secondary-900">
                {address ? `${address.slice(0, 6)}...${address.slice(-4)}` : 'Guest'}
              </p>
              <p className="text-xs text-secondary-500">Connected</p>
            </div>
            
            <div className="flex items-center space-x-2">
              <button className="p-2 text-secondary-400 hover:text-secondary-600 transition-colors">
                <User className="w-5 h-5" />
              </button>
              
              <button
                onClick={handleDisconnect}
                className="p-2 text-secondary-400 hover:text-error-600 transition-colors"
                title="Disconnect"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
