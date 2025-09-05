import React from 'react'
import { TrendingUp, Lock, Zap, BarChart3 } from 'lucide-react'

const DeFi: React.FC = () => {
  const pools = [
    {
      id: 'xrp-usdc',
      name: 'XRP/USDC Pool',
      apy: '15.2%',
      tvl: '$2.4M',
      risk: 'Low',
      color: 'success'
    },
    {
      id: 'xrp-btc',
      name: 'XRP/BTC Pool',
      apy: '22.8%',
      tvl: '$1.8M',
      risk: 'Medium',
      color: 'warning'
    },
    {
      id: 'flash-loan',
      name: 'Flash Loan Pool',
      apy: '35.5%',
      tvl: '$5.2M',
      risk: 'High',
      color: 'error'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-secondary-900">DeFi Dashboard</h1>
        <button className="btn-primary">
          <TrendingUp className="w-4 h-4 mr-2" />
          Create Pool
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-success-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-success-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-600">Total Value Locked</p>
              <p className="text-2xl font-bold text-secondary-900">$9.4M</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-primary-100 rounded-lg">
              <Zap className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-600">Active Pools</p>
              <p className="text-2xl font-bold text-secondary-900">12</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-warning-100 rounded-lg">
              <BarChart3 className="w-6 h-6 text-warning-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-600">Average APY</p>
              <p className="text-2xl font-bold text-secondary-900">24.5%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Pools */}
      <div className="card">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Available Pools</h3>
        <div className="space-y-4">
          {pools.map((pool) => (
            <div key={pool.id} className="flex items-center justify-between p-4 bg-secondary-50 rounded-lg">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-primary rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h4 className="font-medium text-secondary-900">{pool.name}</h4>
                  <p className="text-sm text-secondary-600">TVL: {pool.tvl}</p>
                </div>
              </div>
              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <p className="text-lg font-bold text-success-600">{pool.apy}</p>
                  <p className="text-sm text-secondary-600">APY</p>
                </div>
                <div className={`badge ${
                  pool.color === 'success' ? 'badge-success' :
                  pool.color === 'warning' ? 'badge-warning' :
                  'badge-error'
                }`}>
                  {pool.risk} Risk
                </div>
                <button className="btn-primary">Stake</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default DeFi
