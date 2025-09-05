import React, { useState } from 'react'
import { TrendingUp, Lock, Zap, Users } from 'lucide-react'

const DeFi: React.FC = () => {
  const [activeTab, setActiveTab] = useState('pools')

  const yieldPools = [
    {
      name: 'XRP/USD Pool',
      apy: '12.5%',
      tvl: '$2.4M',
      tokens: ['XRP', 'USD'],
      risk: 'Low'
    },
    {
      name: 'BTC/ETH Pool',
      apy: '18.2%',
      tvl: '$1.8M',
      tokens: ['BTC', 'ETH'],
      risk: 'Medium'
    },
    {
      name: 'Stablecoin Pool',
      apy: '8.7%',
      tvl: '$3.2M',
      tokens: ['USDC', 'USDT', 'DAI'],
      risk: 'Low'
    }
  ]

  const lendingPools = [
    {
      asset: 'XRP',
      supplyRate: '5.2%',
      borrowRate: '7.8%',
      totalSupply: '$1.2M',
      totalBorrow: '$890K',
      utilization: '74%'
    },
    {
      asset: 'BTC',
      supplyRate: '3.1%',
      borrowRate: '5.5%',
      totalSupply: '$2.1M',
      totalBorrow: '$1.4M',
      utilization: '67%'
    },
    {
      asset: 'ETH',
      supplyRate: '4.8%',
      borrowRate: '6.9%',
      totalSupply: '$1.8M',
      totalBorrow: '$1.1M',
      utilization: '61%'
    }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">DeFi</h1>
        <p className="text-gray-600">Explore decentralized finance protocols on XRPL</p>
      </div>

      {/* DeFi Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {['pools', 'lending', 'staking', 'farming'].map((tab) => (
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
          {activeTab === 'pools' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {yieldPools.map((pool, index) => (
                  <div key={index} className="bg-gray-50 p-6 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">{pool.name}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        pool.risk === 'Low' ? 'bg-green-100 text-green-800' :
                        pool.risk === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {pool.risk} Risk
                      </span>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">APY</span>
                        <span className="font-semibold text-green-600">{pool.apy}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">TVL</span>
                        <span className="font-semibold text-gray-900">{pool.tvl}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tokens</span>
                        <span className="font-semibold text-gray-900">{pool.tokens.join('/')}</span>
                      </div>
                    </div>
                    
                    <button className="w-full mt-4 py-2 bg-primary-600 text-white font-medium rounded-md hover:bg-primary-700 transition-colors">
                      Add Liquidity
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'lending' && (
            <div className="space-y-6">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Asset
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Supply Rate
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Borrow Rate
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Total Supply
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Utilization
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {lendingPools.map((pool, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
                              <span className="text-sm font-medium text-primary-700">{pool.asset[0]}</span>
                            </div>
                            <span className="ml-3 text-sm font-medium text-gray-900">{pool.asset}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                          {pool.supplyRate}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-medium">
                          {pool.borrowRate}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {pool.totalSupply}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {pool.utilization}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <button className="text-primary-600 hover:text-primary-900">Supply</button>
                            <button className="text-red-600 hover:text-red-900">Borrow</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'staking' && (
            <div className="text-center py-12">
              <Lock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Staking Coming Soon</h3>
              <p className="text-gray-600">Stake your tokens to earn rewards</p>
            </div>
          )}

          {activeTab === 'farming' && (
            <div className="text-center py-12">
              <Zap className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Yield Farming Coming Soon</h3>
              <p className="text-gray-600">Farm rewards by providing liquidity</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DeFi
