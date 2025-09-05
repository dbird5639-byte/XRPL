import React from 'react'
import { TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react'

const Home: React.FC = () => {
  const stats = [
    { name: 'Total Volume', value: '$2.4M', change: '+12%', changeType: 'positive' },
    { name: 'Active Users', value: '1,234', change: '+8%', changeType: 'positive' },
    { name: 'Total Pairs', value: '156', change: '+3%', changeType: 'positive' },
    { name: '24h Volume', value: '$456K', change: '-2%', changeType: 'negative' },
  ]

  const topPairs = [
    { pair: 'XRP/USD', price: '$0.52', change: '+5.2%', volume: '$234K' },
    { pair: 'BTC/USD', price: '$42,150', change: '+2.1%', volume: '$189K' },
    { pair: 'ETH/USD', price: '$2,650', change: '-1.3%', volume: '$156K' },
    { pair: 'ADA/USD', price: '$0.38', change: '+3.7%', volume: '$98K' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome to XRPL DEX Platform</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
              <div className={`flex items-center text-sm ${
                stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
              }`}>
                {stat.changeType === 'positive' ? (
                  <TrendingUp className="h-4 w-4 mr-1" />
                ) : (
                  <TrendingDown className="h-4 w-4 mr-1" />
                )}
                {stat.change}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Top Trading Pairs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Top Trading Pairs</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pair
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  24h Change
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Volume
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {topPairs.map((pair) => (
                <tr key={pair.pair} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {pair.pair}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {pair.price}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                    pair.change.startsWith('+') ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {pair.change}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {pair.volume}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">Trade</h3>
              <p className="text-gray-600">Start trading on XRPL DEX</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">DeFi</h3>
              <p className="text-gray-600">Explore DeFi protocols</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">Analytics</h3>
              <p className="text-gray-600">View market analytics</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
