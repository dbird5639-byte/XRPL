import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  Database, 
  Bot, 
  Zap, 
  Store, 
  Settings,
  Brain
} from 'lucide-react'

const Sidebar: React.FC = () => {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Dataset Catalog', href: '/datasets', icon: Database },
    { name: 'Agent Builder', href: '/agents', icon: Bot },
    { name: 'Automation Studio', href: '/automation', icon: Zap },
    { name: 'Marketplace', href: '/marketplace', icon: Store },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  return (
    <div className="w-64 bg-white shadow-lg">
      <div className="p-6">
        <div className="flex items-center space-x-3">
          <Brain className="h-8 w-8 text-primary-600" />
          <h1 className="text-xl font-bold text-gray-900">XRPL AI</h1>
        </div>
        <p className="text-sm text-gray-600 mt-1">On-Chain LLM Framework</p>
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
      
      <div className="absolute bottom-0 w-64 p-6 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          <p>Powered by XRPL</p>
          <p>Ripple Approved Datasets</p>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
