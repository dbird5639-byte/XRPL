import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  TrendingUp, 
  Coins, 
  Image, 
  PieChart, 
  Settings,
  Wallet
} from 'lucide-react'

const Sidebar: React.FC = () => {
  const location = useLocation()

  const navigation = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Trading', href: '/trading', icon: TrendingUp },
    { name: 'DeFi', href: '/defi', icon: Coins },
    { name: 'NFTs', href: '/nfts', icon: Image },
    { name: 'Portfolio', href: '/portfolio', icon: PieChart },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  return (
    <div className="w-64 bg-white shadow-lg">
      <div className="p-6">
        <div className="flex items-center space-x-3">
          <Wallet className="h-8 w-8 text-primary-600" />
          <h1 className="text-xl font-bold text-gray-900">XRPL DEX</h1>
        </div>
      </div>
      
      <nav className="mt-6">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center px-6 py-3 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </div>
  )
}

export default Sidebar
