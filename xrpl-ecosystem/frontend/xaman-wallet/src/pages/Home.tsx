import React, { useEffect, useState } from 'react'
import { ArrowUpRight, ArrowDownLeft, TrendingUp, Activity, Zap } from 'lucide-react'
import { useWalletStore } from '../stores/walletStore'
import { useXRPLStore } from '../stores/xrplStore'
import { useQuery } from '@tanstack/react-query'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const Home: React.FC = () => {
  const { address, balance } = useWalletStore()
  const { client, getAccountInfo } = useXRPLStore()
  const [recentTransactions, setRecentTransactions] = useState([])

  // Fetch account info
  const { data: accountInfo, isLoading } = useQuery({
    queryKey: ['accountInfo', address],
    queryFn: () => address ? getAccountInfo(address) : null,
    enabled: !!address,
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  // Mock data for charts
  const portfolioData = [
    { name: 'Jan', value: 1000 },
    { name: 'Feb', value: 1200 },
    { name: 'Mar', value: 1100 },
    { name: 'Apr', value: 1400 },
    { name: 'May', value: 1600 },
    { name: 'Jun', value: 1800 },
  ]

  const stats = [
    {
      name: 'Total Balance',
      value: balance ? `${parseFloat(balance).toFixed(2)} XRP` : '0.00 XRP',
      change: '+12.5%',
      changeType: 'positive' as const,
      icon: Zap,
    },
    {
      name: 'DeFi Positions',
      value: '3',
      change: '+2',
      changeType: 'positive' as const,
      icon: TrendingUp,
    },
    {
      name: 'Active Trades',
      value: '7',
      change: '-1',
      changeType: 'negative' as const,
      icon: Activity,
    },
    {
      name: 'NFTs Owned',
      value: '12',
      change: '+3',
      changeType: 'positive' as const,
      icon: ArrowUpRight,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-primary rounded-2xl p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Welcome back!</h1>
        <p className="text-primary-100 mb-4">
          Your XRPL portfolio is performing well today
        </p>
        <div className="flex items-center space-x-4">
          <div className="bg-white/20 rounded-lg px-4 py-2">
            <p className="text-sm text-primary-100">Network</p>
            <p className="font-semibold">Testnet</p>
          </div>
          <div className="bg-white/20 rounded-lg px-4 py-2">
            <p className="text-sm text-primary-100">Address</p>
            <p className="font-mono text-sm">
              {address ? `${address.slice(0, 8)}...${address.slice(-8)}` : 'Not connected'}
            </p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary-600 mb-1">{stat.name}</p>
                <p className="text-2xl font-bold text-secondary-900">{stat.value}</p>
                <p className={`text-sm ${
                  stat.changeType === 'positive' ? 'text-success-600' : 'text-error-600'
                }`}>
                  {stat.change} from last month
                </p>
              </div>
              <div className={`p-3 rounded-lg ${
                stat.name === 'Total Balance' ? 'bg-primary-100' :
                stat.name === 'DeFi Positions' ? 'bg-success-100' :
                stat.name === 'Active Trades' ? 'bg-warning-100' :
                'bg-secondary-100'
              }`}>
                <stat.icon className={`w-6 h-6 ${
                  stat.name === 'Total Balance' ? 'text-primary-600' :
                  stat.name === 'DeFi Positions' ? 'text-success-600' :
                  stat.name === 'Active Trades' ? 'text-warning-600' :
                  'text-secondary-600'
                }`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Portfolio Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Portfolio Value</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={portfolioData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: '#f8fafc'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#0ea5e9" 
                  strokeWidth={2}
                  dot={{ fill: '#0ea5e9', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="card">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {[
              { type: 'send', amount: '100 XRP', to: 'rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH', time: '2 min ago' },
              { type: 'receive', amount: '50 XRP', from: 'rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe', time: '1 hour ago' },
              { type: 'defi', amount: 'Staked 200 XRP', pool: 'XRP/USDC Pool', time: '3 hours ago' },
              { type: 'trade', amount: 'Bought 1000 USDC', price: '0.52 XRP', time: '5 hours ago' },
            ].map((tx, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-secondary-50 rounded-lg">
                <div className={`p-2 rounded-lg ${
                  tx.type === 'send' ? 'bg-error-100' :
                  tx.type === 'receive' ? 'bg-success-100' :
                  tx.type === 'defi' ? 'bg-primary-100' :
                  'bg-warning-100'
                }`}>
                  {tx.type === 'send' ? (
                    <ArrowUpRight className="w-4 h-4 text-error-600" />
                  ) : tx.type === 'receive' ? (
                    <ArrowDownLeft className="w-4 h-4 text-success-600" />
                  ) : tx.type === 'defi' ? (
                    <TrendingUp className="w-4 h-4 text-primary-600" />
                  ) : (
                    <Activity className="w-4 h-4 text-warning-600" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-secondary-900">{tx.amount}</p>
                  <p className="text-xs text-secondary-500">
                    {tx.to || tx.from || tx.pool || tx.price}
                  </p>
                </div>
                <p className="text-xs text-secondary-500">{tx.time}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="btn-primary">
            <ArrowUpRight className="w-4 h-4 mr-2" />
            Send
          </button>
          <button className="btn-outline">
            <ArrowDownLeft className="w-4 h-4 mr-2" />
            Receive
          </button>
          <button className="btn-outline">
            <TrendingUp className="w-4 h-4 mr-2" />
            DeFi
          </button>
          <button className="btn-outline">
            <Activity className="w-4 h-4 mr-2" />
            Trade
          </button>
        </div>
      </div>
    </div>
  )
}

export default Home
