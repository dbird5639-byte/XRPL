import React from 'react'
import { Zap } from 'lucide-react'

const LoadingScreen: React.FC = () => {
  return (
    <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-6 animate-pulse">
          <Zap className="w-8 h-8 text-white" />
        </div>
        
        <h1 className="text-2xl font-bold text-secondary-900 mb-2">xAman Wallet</h1>
        <p className="text-secondary-600 mb-8">Initializing your wallet...</p>
        
        <div className="flex items-center justify-center space-x-2">
          <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
          <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
        </div>
      </div>
    </div>
  )
}

export default LoadingScreen
