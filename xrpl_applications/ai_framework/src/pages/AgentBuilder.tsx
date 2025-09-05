import React, { useState } from 'react'
import { Plus, Bot, Database, Settings, Play, Save, Trash2, Copy, Eye } from 'lucide-react'

const AgentBuilder: React.FC = () => {
  const [activeTab, setActiveTab] = useState('create')
  const [selectedDatasets, setSelectedDatasets] = useState<number[]>([])
  const [agentConfig, setAgentConfig] = useState({
    name: '',
    description: '',
    purpose: '',
    configuration: ''
  })

  const availableDatasets = [
    { id: 1, name: 'Financial Market Data', category: 'finance', price: '500 XRP', quality: 95 },
    { id: 2, name: 'Smart Contract Templates', category: 'development', price: '300 XRP', quality: 92 },
    { id: 3, name: 'NFT Metadata Collection', category: 'nft', price: '200 XRP', quality: 85 },
    { id: 4, name: 'DeFi Protocol Analytics', category: 'defi', price: '400 XRP', quality: 90 },
    { id: 5, name: 'Healthcare Records', category: 'healthcare', price: '750 XRP', quality: 88 }
  ]

  const userAgents = [
    {
      id: 1,
      name: 'DeFi Strategy Bot',
      description: 'Automated DeFi strategy optimization and execution',
      purpose: 'Trading and yield farming optimization',
      status: 'active',
      datasets: 3,
      usageCount: 1247,
      revenue: '2,340 XRP',
      createdAt: '2024-01-10',
      lastUsed: '2024-01-20'
    },
    {
      id: 2,
      name: 'NFT Generator',
      description: 'AI-powered NFT creation and metadata generation',
      purpose: 'Content creation and NFT marketplace automation',
      status: 'active',
      datasets: 2,
      usageCount: 892,
      revenue: '1,680 XRP',
      createdAt: '2024-01-12',
      lastUsed: '2024-01-19'
    },
    {
      id: 3,
      name: 'Trading Assistant',
      description: 'Market analysis and trading signal generation',
      purpose: 'Financial market analysis and trading automation',
      status: 'deploying',
      datasets: 4,
      usageCount: 0,
      revenue: '0 XRP',
      createdAt: '2024-01-18',
      lastUsed: null
    }
  ]

  const handleDatasetToggle = (datasetId: number) => {
    setSelectedDatasets(prev => 
      prev.includes(datasetId) 
        ? prev.filter(id => id !== datasetId)
        : [...prev, datasetId]
    )
  }

  const calculateTotalCost = () => {
    return selectedDatasets.reduce((total, datasetId) => {
      const dataset = availableDatasets.find(d => d.id === datasetId)
      return total + (dataset ? parseInt(dataset.price) : 0)
    }, 0)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'deploying':
        return 'bg-blue-100 text-blue-800'
      case 'inactive':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Agent Builder</h1>
          <p className="text-gray-600">Create and manage your AI agents with custom datasets</p>
        </div>
        <button 
          onClick={() => setActiveTab('create')}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Create New Agent</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'create', name: 'Create Agent', icon: Plus },
            { id: 'manage', name: 'My Agents', icon: Bot }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {activeTab === 'create' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Agent Configuration */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Configuration</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Agent Name</label>
                  <input
                    type="text"
                    value={agentConfig.name}
                    onChange={(e) => setAgentConfig(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Enter agent name..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={agentConfig.description}
                    onChange={(e) => setAgentConfig(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Describe what your agent does..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Purpose</label>
                  <input
                    type="text"
                    value={agentConfig.purpose}
                    onChange={(e) => setAgentConfig(prev => ({ ...prev, purpose: e.target.value }))}
                    placeholder="What is the main purpose of this agent?"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Configuration (JSON)</label>
                  <textarea
                    value={agentConfig.configuration}
                    onChange={(e) => setAgentConfig(prev => ({ ...prev, configuration: e.target.value }))}
                    placeholder='{"model": "gpt-4", "temperature": 0.7, "max_tokens": 1000}'
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
                  />
                </div>
              </div>
            </div>

            {/* Dataset Selection */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Datasets</h3>
              <p className="text-sm text-gray-600 mb-4">Choose the datasets your agent will use for training and operation</p>
              
              <div className="space-y-3">
                {availableDatasets.map((dataset) => (
                  <div key={dataset.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                    <div className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={selectedDatasets.includes(dataset.id)}
                        onChange={() => handleDatasetToggle(dataset.id)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <div>
                        <h4 className="font-medium text-gray-900">{dataset.name}</h4>
                        <p className="text-sm text-gray-600 capitalize">{dataset.category} • Quality: {dataset.quality}%</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-primary-600">{dataset.price}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Cost Summary & Actions */}
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Summary</h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Agent Creation Fee</span>
                  <span className="font-medium">50 XRP</span>
                </div>
                
                {selectedDatasets.map(datasetId => {
                  const dataset = availableDatasets.find(d => d.id === datasetId)
                  return (
                    <div key={datasetId} className="flex justify-between">
                      <span className="text-gray-600">{dataset?.name}</span>
                      <span className="font-medium">{dataset?.price}</span>
                    </div>
                  )
                })}
                
                <div className="border-t border-gray-200 pt-3">
                  <div className="flex justify-between">
                    <span className="font-semibold text-gray-900">Total Cost</span>
                    <span className="font-bold text-primary-600">{calculateTotalCost() + 50} XRP</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 space-y-3">
                <button className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 flex items-center justify-center space-x-2">
                  <Save className="h-4 w-4" />
                  <span>Create Agent</span>
                </button>
                <button className="w-full border border-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-50">
                  Save as Draft
                </button>
              </div>
            </div>

            {/* Agent Templates */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Templates</h3>
              <div className="space-y-3">
                <button className="w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <h4 className="font-medium text-gray-900">DeFi Trading Bot</h4>
                  <p className="text-sm text-gray-600">Automated trading strategies</p>
                </button>
                <button className="w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <h4 className="font-medium text-gray-900">NFT Generator</h4>
                  <p className="text-sm text-gray-600">AI-powered NFT creation</p>
                </button>
                <button className="w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <h4 className="font-medium text-gray-900">Code Reviewer</h4>
                  <p className="text-sm text-gray-600">Smart contract auditing</p>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'manage' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {userAgents.map((agent) => (
              <div key={agent.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-primary-100 rounded-lg">
                        <Bot className="h-6 w-6 text-primary-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(agent.status)}`}>
                          {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                        </span>
                      </div>
                    </div>
                    <div className="flex space-x-1">
                      <button className="p-1 text-gray-400 hover:text-gray-600">
                        <Eye className="h-4 w-4" />
                      </button>
                      <button className="p-1 text-gray-400 hover:text-gray-600">
                        <Copy className="h-4 w-4" />
                      </button>
                      <button className="p-1 text-gray-400 hover:text-red-600">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 mb-4">{agent.description}</p>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Purpose:</span>
                      <span className="text-gray-900">{agent.purpose}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Datasets:</span>
                      <span className="text-gray-900">{agent.datasets}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Usage:</span>
                      <span className="text-gray-900">{agent.usageCount.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Revenue:</span>
                      <span className="text-gray-900 font-semibold">{agent.revenue}</span>
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    {agent.status === 'active' && (
                      <button className="flex-1 bg-primary-600 text-white py-2 px-3 rounded-lg hover:bg-primary-700 flex items-center justify-center space-x-1">
                        <Play className="h-3 w-3" />
                        <span className="text-sm">Deploy</span>
                      </button>
                    )}
                    <button className="px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center justify-center">
                      <Settings className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default AgentBuilder
