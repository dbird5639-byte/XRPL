import React, { useState } from 'react'
import { ArrowUpDown, TrendingUp, TrendingDown } from 'lucide-react'

const Trading: React.FC = () => {
  const [activeTab, setActiveTab] = useState('spot')
  const [orderType, setOrderType] = useState('market')

  const orderBook = {
    bids: [
      { price: 0.5215, amount: 1250.5, total: 652.19 },
      { price: 0.5210, amount: 890.2, total: 463.79 },
      { price: 0.5205, amount: 2100.8, total: 1093.47 },
      { price: 0.5200, amount: 1500.0, total: 780.00 },
      { price: 0.5195, amount: 3200.5, total: 1664.26 },
    ],
    asks: [
      { price: 0.5220, amount: 980.3, total: 511.72 },
      { price: 0.5225, amount: 1450.7, total: 757.99 },
      { price: 0.5230, amount: 2100.2, total: 1098.40 },
      { price: 0.5235, amount: 1800.9, total: 942.77 },
      { price: 0.5240, amount: 2500.1, total: 1310.05 },
    ]
  }

  const recentTrades = [
    { price: 0.5218, amount: 150.5, time: '14:32:15', type: 'buy' },
    { price: 0.5215, amount: 89.2, time: '14:31:42', type: 'sell' },
    { price: 0.5220, amount: 210.8, time: '14:31:18', type: 'buy' },
    { price: 0.5210, amount: 75.3, time: '14:30:55', type: 'sell' },
    { price: 0.5215, amount: 180.7, time: '14:30:23', type: 'buy' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Trading</h1>
        <p className="text-gray-600">Trade on XRPL DEX with advanced features</p>
      </div>

      {/* Trading Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {['spot', 'futures', 'options'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Order Book */}
            <div className="lg:col-span-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Book</h3>
              <div className="space-y-2">
                {/* Asks */}
                <div className="space-y-1">
                  {orderBook.asks.map((ask, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-red-600">{ask.price}</span>
                      <span className="text-gray-900">{ask.amount}</span>
                      <span className="text-gray-500">{ask.total}</span>
                    </div>
                  ))}
                </div>
                
                {/* Spread */}
                <div className="border-t border-b border-gray-200 py-2">
                  <div className="flex justify-between text-sm font-medium">
                    <span className="text-gray-900">Spread</span>
                    <span className="text-gray-900">0.0005 (0.10%)</span>
                  </div>
                </div>
                
                {/* Bids */}
                <div className="space-y-1">
                  {orderBook.bids.map((bid, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-green-600">{bid.price}</span>
                      <span className="text-gray-900">{bid.amount}</span>
                      <span className="text-gray-500">{bid.total}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Trading Interface */}
            <div className="lg:col-span-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Place Order</h3>
              
              {/* Order Type */}
              <div className="mb-4">
                <div className="flex space-x-2">
                  {['market', 'limit', 'stop'].map((type) => (
                    <button
                      key={type}
                      onClick={() => setOrderType(type)}
                      className={`px-3 py-1 text-sm font-medium rounded-md capitalize ${
                        orderType === type
                          ? 'bg-primary-100 text-primary-700'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              {/* Buy/Sell Tabs */}
              <div className="flex mb-4">
                <button className="flex-1 py-2 px-4 bg-green-100 text-green-700 font-medium rounded-l-md">
                  Buy
                </button>
                <button className="flex-1 py-2 px-4 bg-gray-100 text-gray-700 font-medium rounded-r-md">
                  Sell
                </button>
              </div>

              {/* Order Form */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Amount
                  </label>
                  <input
                    type="number"
                    placeholder="0.00"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Price
                  </label>
                  <input
                    type="number"
                    placeholder="0.00"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Total
                  </label>
                  <input
                    type="number"
                    placeholder="0.00"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <button className="w-full py-3 bg-primary-600 text-white font-medium rounded-md hover:bg-primary-700 transition-colors">
                  Buy XRP
                </button>
              </div>
            </div>

            {/* Recent Trades */}
            <div className="lg:col-span-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Trades</h3>
              <div className="space-y-2">
                {recentTrades.map((trade, index) => (
                  <div key={index} className="flex justify-between items-center text-sm">
                    <span className={`font-medium ${
                      trade.type === 'buy' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {trade.price}
                    </span>
                    <span className="text-gray-900">{trade.amount}</span>
                    <span className="text-gray-500">{trade.time}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Trading
