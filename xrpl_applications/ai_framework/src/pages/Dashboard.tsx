import React, { useState } from 'react'
import { TrendingUp, Database, Bot, Zap, Users, DollarSign, Clock, CheckCircle } from 'lucide-react'

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview')

  const stats = [
    { name: 'Total Datasets', value: '1,247', change: '+12%', changeType: 'positive', icon: Database },
    { name: 'Active Agents', value: '89', change: '+8%', changeType: 'positive', icon: Bot },
    { name: 'Automation Tasks', value: '2,156', change: '+23%', changeType: 'positive', icon: Zap },
    { name: 'Total Revenue', value: '45,230 XRP', change: '+15%', changeType: 'positive', icon: DollarSign },
  ]

  const recentDatasets = [
    { name: 'Financial Market Data', category: 'Finance', price: '500 XRP', status: 'Approved', quality: 95 },
    { name: 'Healthcare Records', category: 'Healthcare', price: '750 XRP', status: 'Pending', quality: 88 },
    { name: 'Smart Contract Templates', category: 'Development', price: '300 XRP', status: 'Approved', quality: 92 },
    { name: 'NFT Metadata', category: 'NFTs', price: '200 XRP', status: 'Approved', quality: 85 },
  ]

  const recentAgents = [
    { name: 'DeFi Strategy Bot', purpose: 'Automated DeFi strategies', datasets: 3, status: 'Active' },
    { name: 'NFT Generator', purpose: 'AI-powered NFT creation', datasets: 2, status: 'Active' },
    { name: 'Trading Assistant', purpose: 'Market analysis and trading', datasets: 4, status: 'Deploying' },
    { name: 'Code Reviewer', purpose: 'Smart contract auditing', datasets: 1, status: 'Active' },
  ]

  const automationTasks = [
    { name: 'Daily Portfolio Rebalancing', type: 'DeFi Strategy', status: 'Completed', nextRun: '2 hours' },
    { name: 'NFT Collection Analysis', type: 'Data Analysis', status: 'Running', nextRun: 'Now' },
    { name: 'Market Sentiment Report', type: 'Trading Bot', status: 'Scheduled', nextRun: '6 hours' },
    { name: 'Smart Contract Deployment', type: 'Development', status: 'Failed', nextRun: 'Retry in 1 hour' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Framework Dashboard</h1>
        <p className="text-gray-600">Monitor your AI agents, datasets, and automation tasks</p>
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
                <TrendingUp className="h-4 w-4 mr-1" />
                {stat.change}
              </div>
            </div>
            <div className="mt-4">
              <stat.icon className="h-8 w-8 text-primary-600" />
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {['overview', 'datasets', 'agents', 'automation'].map((tab) => (
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
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recent Datasets */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Datasets</h3>
                <div className="space-y-3">
                  {recentDatasets.map((dataset, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">{dataset.name}</p>
                        <p className="text-sm text-gray-600">{dataset.category} • {dataset.price}</p>
                      </div>
                      <div className="text-right">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          dataset.status === 'Approved' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {dataset.status}
                        </span>
                        <p className="text-sm text-gray-600 mt-1">Quality: {dataset.quality}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent Agents */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Agents</h3>
                <div className="space-y-3">
                  {recentAgents.map((agent, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">{agent.name}</p>
                        <p className="text-sm text-gray-600">{agent.purpose}</p>
                      </div>
                      <div className="text-right">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          agent.status === 'Active' ? 'bg-green-100 text-green-800' : 
                          agent.status === 'Deploying' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {agent.status}
                        </span>
                        <p className="text-sm text-gray-600 mt-1">{agent.datasets} datasets</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'automation' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Automation Tasks</h3>
              <div className="space-y-3">
                {automationTasks.map((task, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className={`p-2 rounded-full ${
                        task.status === 'Completed' ? 'bg-green-100' :
                        task.status === 'Running' ? 'bg-blue-100' :
                        task.status === 'Scheduled' ? 'bg-yellow-100' : 'bg-red-100'
                      }`}>
                        {task.status === 'Completed' ? <CheckCircle className="h-5 w-5 text-green-600" /> :
                         task.status === 'Running' ? <Clock className="h-5 w-5 text-blue-600" /> :
                         <Clock className="h-5 w-5 text-yellow-600" />}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{task.name}</p>
                        <p className="text-sm text-gray-600">{task.type}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        task.status === 'Completed' ? 'bg-green-100 text-green-800' :
                        task.status === 'Running' ? 'bg-blue-100 text-blue-800' :
                        task.status === 'Scheduled' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {task.status}
                      </span>
                      <p className="text-sm text-gray-600 mt-1">Next: {task.nextRun}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <Database className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">Submit Dataset</h3>
              <p className="text-gray-600">Contribute to the AI ecosystem</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <Bot className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">Create Agent</h3>
              <p className="text-gray-600">Build your AI agent</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <Zap className="h-8 w-8 text-primary-600" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-gray-900">Automate Task</h3>
              <p className="text-gray-600">Set up automation</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
