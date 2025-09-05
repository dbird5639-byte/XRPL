import React, { useState } from 'react'
import { Search, Filter, Star, TrendingUp, Users, DollarSign, Clock, CheckCircle } from 'lucide-react'

const Marketplace: React.FC = () => {
  const [activeTab, setActiveTab] = useState('agents')
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState('popular')

  const agents = [
    {
      id: 1,
      name: 'DeFi Yield Optimizer',
      description: 'Automatically finds and executes the best yield farming opportunities across multiple protocols',
      creator: '0x1234...5678',
      price: '100 XRP',
      rating: 4.9,
      reviews: 127,
      usageCount: 2847,
      revenue: '12,450 XRP',
      category: 'defi',
      tags: ['yield farming', 'automation', 'multi-protocol'],
      createdAt: '2024-01-10',
      lastUpdated: '2024-01-18'
    },
    {
      id: 2,
      name: 'NFT Market Analyzer',
      description: 'Advanced NFT market analysis with floor price tracking and trend prediction',
      creator: '0x2345...6789',
      price: '75 XRP',
      rating: 4.7,
      reviews: 89,
      usageCount: 1923,
      revenue: '8,920 XRP',
      category: 'nft',
      tags: ['nft', 'analysis', 'trending'],
      createdAt: '2024-01-12',
      lastUpdated: '2024-01-19'
    },
    {
      id: 3,
      name: 'Smart Contract Auditor Pro',
      description: 'Professional-grade smart contract security auditing with vulnerability detection',
      creator: '0x3456...7890',
      price: '150 XRP',
      rating: 4.8,
      reviews: 156,
      usageCount: 3241,
      revenue: '18,750 XRP',
      category: 'security',
      tags: ['security', 'auditing', 'vulnerability'],
      createdAt: '2024-01-08',
      lastUpdated: '2024-01-20'
    },
    {
      id: 4,
      name: 'Trading Signal Generator',
      description: 'AI-powered trading signals with backtesting and risk management',
      creator: '0x4567...8901',
      price: '120 XRP',
      rating: 4.6,
      reviews: 203,
      usageCount: 4567,
      revenue: '22,340 XRP',
      category: 'trading',
      tags: ['trading', 'signals', 'backtesting'],
      createdAt: '2024-01-05',
      lastUpdated: '2024-01-17'
    }
  ]

  const templates = [
    {
      id: 1,
      name: 'Portfolio Rebalancer',
      description: 'Automated portfolio rebalancing based on market conditions',
      creator: '0x5678...9012',
      price: '50 XRP',
      rating: 4.5,
      usageCount: 892,
      category: 'defi',
      tags: ['portfolio', 'rebalancing', 'automation']
    },
    {
      id: 2,
      name: 'NFT Collection Monitor',
      description: 'Monitor NFT collections for price changes and opportunities',
      creator: '0x6789...0123',
      price: '30 XRP',
      rating: 4.3,
      usageCount: 567,
      category: 'nft',
      tags: ['monitoring', 'nft', 'alerts']
    },
    {
      id: 3,
      name: 'DeFi Risk Assessor',
      description: 'Assess risk levels of DeFi protocols and positions',
      creator: '0x7890...1234',
      price: '80 XRP',
      rating: 4.7,
      usageCount: 1234,
      category: 'defi',
      tags: ['risk', 'assessment', 'defi']
    }
  ]

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'defi':
        return 'bg-purple-100 text-purple-800'
      case 'nft':
        return 'bg-pink-100 text-pink-800'
      case 'trading':
        return 'bg-green-100 text-green-800'
      case 'security':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const filteredAgents = agents.filter(agent =>
    agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    agent.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    agent.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  const filteredTemplates = templates.filter(template =>
    template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    template.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Marketplace</h1>
          <p className="text-gray-600">Discover and purchase AI agents and automation templates</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-600">
            <span className="font-semibold">{agents.length}</span> agents • <span className="font-semibold">{templates.length}</span> templates
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search agents and templates..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div className="flex gap-4">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="popular">Most Popular</option>
              <option value="newest">Newest</option>
              <option value="rating">Highest Rated</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
              <option value="revenue">Highest Revenue</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'agents', name: 'AI Agents' },
            { id: 'templates', name: 'Templates' },
            { id: 'trending', name: 'Trending' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {activeTab === 'agents' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredAgents.map((agent) => (
            <div key={agent.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(agent.category)}`}>
                        {agent.category.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{agent.description}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-primary-600">{agent.price}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="flex items-center space-x-2">
                    <Star className="h-4 w-4 text-yellow-400 fill-current" />
                    <span className="text-sm font-medium text-gray-900">{agent.rating}</span>
                    <span className="text-sm text-gray-500">({agent.reviews} reviews)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Users className="h-4 w-4 text-gray-400" />
                    <span className="text-sm text-gray-900">{agent.usageCount.toLocaleString()} uses</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <DollarSign className="h-4 w-4 text-green-500" />
                    <span className="text-sm text-gray-900">{agent.revenue} revenue</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-gray-400" />
                    <span className="text-sm text-gray-900">Updated {agent.lastUpdated}</span>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1 mb-4">
                  {agent.tags.map((tag, index) => (
                    <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    by {agent.creator}
                  </div>
                  <div className="flex space-x-2">
                    <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                      Preview
                    </button>
                    <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
                      Purchase
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'templates' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.map((template) => (
            <div key={template.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{template.name}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(template.category)}`}>
                        {template.category.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold text-primary-600">{template.price}</p>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Rating:</span>
                    <div className="flex items-center space-x-1">
                      <Star className="h-4 w-4 text-yellow-400 fill-current" />
                      <span className="font-medium text-gray-900">{template.rating}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Usage:</span>
                    <span className="text-gray-900">{template.usageCount.toLocaleString()} times</span>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1 mb-4">
                  {template.tags.map((tag, index) => (
                    <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    by {template.creator}
                  </div>
                  <div className="flex space-x-2">
                    <button className="px-3 py-1 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm">
                      Preview
                    </button>
                    <button className="px-3 py-1 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm">
                      Use Template
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'trending' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center space-x-3 mb-4">
                <TrendingUp className="h-6 w-6 text-green-600" />
                <h3 className="text-lg font-semibold text-gray-900">Trending Agents</h3>
              </div>
              <div className="space-y-3">
                {agents.slice(0, 3).map((agent, index) => (
                  <div key={agent.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{agent.name}</p>
                        <p className="text-xs text-gray-500">{agent.usageCount} uses</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-primary-600">{agent.price}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center space-x-3 mb-4">
                <Star className="h-6 w-6 text-yellow-500" />
                <h3 className="text-lg font-semibold text-gray-900">Top Rated</h3>
              </div>
              <div className="space-y-3">
                {agents.sort((a, b) => b.rating - a.rating).slice(0, 3).map((agent, index) => (
                  <div key={agent.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{agent.name}</p>
                        <div className="flex items-center space-x-1">
                          <Star className="h-3 w-3 text-yellow-400 fill-current" />
                          <p className="text-xs text-gray-500">{agent.rating}</p>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-primary-600">{agent.price}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center space-x-3 mb-4">
                <DollarSign className="h-6 w-6 text-green-600" />
                <h3 className="text-lg font-semibold text-gray-900">Highest Revenue</h3>
              </div>
              <div className="space-y-3">
                {agents.sort((a, b) => parseInt(b.revenue) - parseInt(a.revenue)).slice(0, 3).map((agent, index) => (
                  <div key={agent.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{agent.name}</p>
                        <p className="text-xs text-gray-500">{agent.revenue}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-primary-600">{agent.price}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {(activeTab === 'agents' && filteredAgents.length === 0) || 
       (activeTab === 'templates' && filteredTemplates.length === 0) && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Search className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
          <p className="text-gray-600">Try adjusting your search criteria</p>
        </div>
      )}
    </div>
  )
}

export default Marketplace
