import React, { useState } from 'react'
import { Play, Pause, Square, Plus, Clock, CheckCircle, XCircle, AlertCircle, Settings, Copy, Trash2 } from 'lucide-react'

const AutomationStudio: React.FC = () => {
  const [activeTab, setActiveTab] = useState('tasks')
  const [selectedTask, setSelectedTask] = useState<number | null>(null)

  const automationTasks = [
    {
      id: 1,
      name: 'Daily Portfolio Rebalancing',
      type: 'defi_strategy',
      description: 'Automatically rebalance portfolio based on market conditions',
      status: 'completed',
      lastRun: '2024-01-20 14:30:00',
      nextRun: '2024-01-21 14:30:00',
      frequency: 'daily',
      agents: ['DeFi Strategy Bot'],
      cost: '25 XRP',
      revenue: '45 XRP',
      successRate: 95,
      totalRuns: 20
    },
    {
      id: 2,
      name: 'NFT Collection Analysis',
      type: 'data_analysis',
      description: 'Analyze NFT collections for investment opportunities',
      status: 'running',
      lastRun: '2024-01-20 16:45:00',
      nextRun: '2024-01-20 18:45:00',
      frequency: '2 hours',
      agents: ['NFT Generator', 'Trading Assistant'],
      cost: '15 XRP',
      revenue: '0 XRP',
      successRate: 88,
      totalRuns: 12
    },
    {
      id: 3,
      name: 'Market Sentiment Report',
      type: 'trading_bot',
      description: 'Generate daily market sentiment analysis reports',
      status: 'scheduled',
      lastRun: '2024-01-19 09:00:00',
      nextRun: '2024-01-21 09:00:00',
      frequency: 'daily',
      agents: ['Trading Assistant'],
      cost: '10 XRP',
      revenue: '120 XRP',
      successRate: 92,
      totalRuns: 45
    },
    {
      id: 4,
      name: 'Smart Contract Deployment',
      type: 'smart_contract',
      description: 'Deploy verified smart contracts to testnet',
      status: 'failed',
      lastRun: '2024-01-20 10:15:00',
      nextRun: '2024-01-20 12:15:00',
      frequency: '2 hours',
      agents: ['Code Reviewer'],
      cost: '20 XRP',
      revenue: '0 XRP',
      successRate: 78,
      totalRuns: 8
    }
  ]

  const templates = [
    {
      id: 1,
      name: 'DeFi Yield Optimization',
      description: 'Automatically find and execute the best yield farming opportunities',
      type: 'defi_strategy',
      agents: ['DeFi Strategy Bot'],
      cost: '30 XRP',
      usageCount: 156
    },
    {
      id: 2,
      name: 'NFT Floor Price Monitor',
      description: 'Monitor NFT floor prices and execute buy/sell orders',
      type: 'nft_generation',
      agents: ['NFT Generator'],
      cost: '20 XRP',
      usageCount: 89
    },
    {
      id: 3,
      name: 'Smart Contract Auditor',
      description: 'Automatically audit smart contracts for vulnerabilities',
      type: 'smart_contract',
      agents: ['Code Reviewer'],
      cost: '25 XRP',
      usageCount: 234
    }
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'running':
        return <Play className="h-4 w-4 text-blue-600" />
      case 'scheduled':
        return <Clock className="h-4 w-4 text-yellow-600" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'running':
        return 'bg-blue-100 text-blue-800'
      case 'scheduled':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'defi_strategy':
        return 'bg-purple-100 text-purple-800'
      case 'data_analysis':
        return 'bg-blue-100 text-blue-800'
      case 'trading_bot':
        return 'bg-green-100 text-green-800'
      case 'smart_contract':
        return 'bg-orange-100 text-orange-800'
      case 'nft_generation':
        return 'bg-pink-100 text-pink-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Automation Studio</h1>
          <p className="text-gray-600">Create and manage AI-powered automation tasks</p>
        </div>
        <button className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>Create Task</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'tasks', name: 'My Tasks' },
            { id: 'templates', name: 'Templates' },
            { id: 'analytics', name: 'Analytics' }
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

      {activeTab === 'tasks' && (
        <div className="space-y-6">
          {/* Task Controls */}
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                  <Play className="h-4 w-4" />
                  <span>Run All</span>
                </button>
                <button className="flex items-center space-x-2 px-3 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700">
                  <Pause className="h-4 w-4" />
                  <span>Pause All</span>
                </button>
                <button className="flex items-center space-x-2 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                  <Square className="h-4 w-4" />
                  <span>Stop All</span>
                </button>
              </div>
              <div className="text-sm text-gray-600">
                {automationTasks.length} tasks • {automationTasks.filter(t => t.status === 'running').length} running
              </div>
            </div>
          </div>

          {/* Tasks List */}
          <div className="space-y-4">
            {automationTasks.map((task) => (
              <div key={task.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start space-x-4">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(task.status)}
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{task.name}</h3>
                          <p className="text-sm text-gray-600">{task.description}</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(task.status)}`}>
                        {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                      </span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(task.type)}`}>
                        {task.type.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-500">Last Run</p>
                      <p className="text-sm font-medium text-gray-900">{task.lastRun}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Next Run</p>
                      <p className="text-sm font-medium text-gray-900">{task.nextRun}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Frequency</p>
                      <p className="text-sm font-medium text-gray-900">{task.frequency}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Success Rate</p>
                      <p className="text-sm font-medium text-gray-900">{task.successRate}%</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="text-sm">
                        <span className="text-gray-500">Agents: </span>
                        <span className="text-gray-900">{task.agents.join(', ')}</span>
                      </div>
                      <div className="text-sm">
                        <span className="text-gray-500">Cost: </span>
                        <span className="text-gray-900">{task.cost}</span>
                      </div>
                      <div className="text-sm">
                        <span className="text-gray-500">Revenue: </span>
                        <span className="text-gray-900 font-semibold">{task.revenue}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {task.status === 'running' ? (
                        <button className="px-3 py-1 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 flex items-center space-x-1">
                          <Pause className="h-3 w-3" />
                          <span className="text-sm">Pause</span>
                        </button>
                      ) : (
                        <button className="px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-1">
                          <Play className="h-3 w-3" />
                          <span className="text-sm">Run</span>
                        </button>
                      )}
                      <button className="px-3 py-1 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                        <Settings className="h-4 w-4" />
                      </button>
                      <button className="px-3 py-1 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                        <Copy className="h-4 w-4" />
                      </button>
                      <button className="px-3 py-1 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'templates' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <div key={template.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{template.name}</h3>
                    <p className="text-sm text-gray-600">{template.description}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(template.type)}`}>
                    {template.type.replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                <div className="space-y-3 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Agents:</span>
                    <span className="text-gray-900">{template.agents.join(', ')}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Cost:</span>
                    <span className="text-gray-900 font-semibold">{template.cost}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Usage:</span>
                    <span className="text-gray-900">{template.usageCount} times</span>
                  </div>
                </div>

                <button className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700">
                  Use Template
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Performance</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Tasks</span>
                <span className="font-semibold text-gray-900">{automationTasks.length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Active Tasks</span>
                <span className="font-semibold text-green-600">{automationTasks.filter(t => t.status === 'running').length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Average Success Rate</span>
                <span className="font-semibold text-gray-900">
                  {Math.round(automationTasks.reduce((acc, task) => acc + task.successRate, 0) / automationTasks.length)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Revenue</span>
                <span className="font-semibold text-green-600">
                  {automationTasks.reduce((acc, task) => acc + parseInt(task.revenue), 0)} XRP
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Analysis</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Spent</span>
                <span className="font-semibold text-red-600">
                  {automationTasks.reduce((acc, task) => acc + parseInt(task.cost), 0)} XRP
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Net Profit</span>
                <span className="font-semibold text-green-600">
                  {automationTasks.reduce((acc, task) => acc + parseInt(task.revenue) - parseInt(task.cost), 0)} XRP
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">ROI</span>
                <span className="font-semibold text-green-600">
                  {Math.round((automationTasks.reduce((acc, task) => acc + parseInt(task.revenue) - parseInt(task.cost), 0) / 
                   automationTasks.reduce((acc, task) => acc + parseInt(task.cost), 0)) * 100)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AutomationStudio
