import React from 'react'
import { BarChart3, TrendingUp, TrendingDown, Activity } from 'lucide-react'

const Trading: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-secondary-900">Trading Dashboard</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Price Chart</h3>
          <div className="h-64 bg-secondary-100 rounded-lg flex items-center justify-center">
            <BarChart3 className="w-16 h-16 text-secondary-400" />
          </div>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Order Book</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-error-600">Sell Orders</span>
              <span className="text-secondary-600">Price | Amount</span>
            </div>
            {[0.52, 0.51, 0.50].map((price, i) => (
              <div key={i} className="flex justify-between text-sm py-1">
                <span className="text-error-600">{price}</span>
                <span className="text-secondary-600">1,234</span>
              </div>
            ))}
            <div className="border-t border-secondary-200 my-2"></div>
            {[0.49, 0.48, 0.47].map((price, i) => (
              <div key={i} className="flex justify-between text-sm py-1">
                <span className="text-success-600">{price}</span>
                <span className="text-secondary-600">1,234</span>
              </div>
            ))}
            <div className="flex justify-between text-sm">
              <span className="text-success-600">Buy Orders</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Trading
