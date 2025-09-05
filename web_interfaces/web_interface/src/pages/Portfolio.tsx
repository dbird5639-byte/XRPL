import React, { useState } from 'react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, DollarSign, PieChart as PieChartIcon } from 'lucide-react'

const Portfolio: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview')

  const portfolioData = {
    totalValue: 12543.67,
    totalChange: 1247.32,
    totalChangePercent: 11.05,
    assets: [
      { symbol: 'XRP', name: 'XRP', amount: 25000, value: 13000, change: 8.5, color: '#3b82f6' },
      { symbol: 'BTC', name: 'Bitcoin', amount: 0.15, value: 6450, change: 12.3, color: '#f59e0b' },
      { symbol: 'ETH', name: 'Ethereum', amount: 2.5, value: 6625, change: 15.7, color: '#8b5cf6' },
      { symbol: 'ADA', name: 'Cardano', amount: 5000, value: 1900, change: -2.1, color: '#10b981' },
      { symbol: 'USDC', name: 'USD Coin', amount: 1000, value: 1000, change: 0, color: '#6b7280' }
    ]
  }

  const pieData = portfolioData.assets.map(asset => ({
    name: asset.symbol,
    value: asset.value,
    color: asset.color
  }))

  const performanceData = [
    { month: 'Jan', value: 8500 },
    { month: 'Feb', value: 9200 },
    { month: 'Mar', value: 8800 },
    { month: 'Apr', value: 10500 },
    { month: 'May', value: 11200 },
    { month: 'Jun', value: 12543 }
  ]

  const recentTransactions = [
    { type: 'Buy', asset: 'XRP', amount: 1000, price: 0.52, time: '2 hours ago', status: 'Completed' },
    { type: 'Sell', asset: 'BTC', amount: 0.05, price: 43000, time: '1 day ago', status: 'Completed' },
    { type: 'Buy', asset: 'ETH', amount: 1.0, price: 2650, time: '3 days ago', status: 'Completed' },
    { type: 'Stake', asset: 'ADA', amount: 2000, price: 0.38, time: '1 week ago', status: 'Active' }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Portfolio</h1>
        <p className="text-gray-600">Track your investments and performance</p>
      </div>

      {/* Portfolio Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {['overview', 'assets', 'transactions', 'analytics'].map((tab) => (
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
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Portfolio Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gradient-to-r from-primary-500 to-primary-600 p-6 rounded-lg text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-primary-100">Total Portfolio Value</p>
                      <p className="text-3xl font-bold">${portfolioData.totalValue.toLocaleString()}</p>
                    </div>
                    <DollarSign className="h-8 w-8 text-primary-200" />
                  </div>
                </div>
                
                <div className="bg-white p-6 rounded-lg border border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-600">24h Change</p>
                      <p className="text-2xl font-bold text-green-600">+${portfolioData.totalChange.toLocaleString()}</p>
                    </div>
                    <TrendingUp className="h-8 w-8 text-green-500" />
                  </div>
                </div>
                
                <div className="bg-white p-6 rounded-lg border border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-600">24h Change %</p>
                      <p className="text-2xl font-bold text-green-600">+{portfolioData.totalChangePercent}%</p>
                    </div>
                    <TrendingUp className="h-8 w-8 text-green-500" />
                  </div>
                </div>
              </div>

              {/* Portfolio Chart */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-lg border border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Asset Allocation</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={120}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [`$${value}`, 'Value']} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                
                <div className="bg-white p-6 rounded-lg border border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip formatter={(value) => [`$${value}`, 'Value']} />
                      <Bar dataKey="value" fill="#3b82f6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'assets' && (
            <div className="space-y-6">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Asset
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Value
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        24h Change
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {portfolioData.assets.map((asset, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="h-8 w-8 bg-gray-100 rounded-full flex items-center justify-center">
                              <span className="text-sm font-medium text-gray-700">{asset.symbol[0]}</span>
                            </div>
                            <div className="ml-3">
                              <div className="text-sm font-medium text-gray-900">{asset.name}</div>
                              <div className="text-sm text-gray-500">{asset.symbol}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {asset.amount.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${asset.value.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`font-medium ${
                            asset.change >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {asset.change >= 0 ? '+' : ''}{asset.change}%
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <button className="text-primary-600 hover:text-primary-900">Trade</button>
                            <button className="text-gray-600 hover:text-gray-900">Send</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'transactions' && (
            <div className="space-y-6">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Asset
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Price
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {recentTransactions.map((tx, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            tx.type === 'Buy' ? 'bg-green-100 text-green-800' :
                            tx.type === 'Sell' ? 'bg-red-100 text-red-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {tx.type}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {tx.asset}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {tx.amount.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${tx.price.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {tx.time}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            tx.status === 'Completed' ? 'bg-green-100 text-green-800' :
                            tx.status === 'Active' ? 'bg-blue-100 text-blue-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {tx.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="text-center py-12">
              <PieChartIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Advanced Analytics Coming Soon</h3>
              <p className="text-gray-600">Detailed portfolio analytics and insights</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Portfolio
