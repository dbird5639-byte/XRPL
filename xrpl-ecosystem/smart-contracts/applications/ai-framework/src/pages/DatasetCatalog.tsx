import React, { useState } from 'react'
import { Search, Filter, Plus, Download, Eye, Star, Clock, CheckCircle, XCircle } from 'lucide-react'

const DatasetCatalog: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [sortBy, setSortBy] = useState('newest')

  const categories = ['all', 'finance', 'healthcare', 'development', 'nft', 'trading', 'defi', 'gaming']

  const datasets = [
    {
      id: 1,
      name: 'Financial Market Data 2024',
      description: 'Comprehensive financial market data including stocks, crypto, and forex with real-time updates',
      category: 'finance',
      price: '500 XRP',
      size: '2.5 GB',
      quality: 95,
      status: 'approved',
      submitter: '0x1234...5678',
      purchaseCount: 127,
      rating: 4.8,
      tags: ['real-time', 'crypto', 'stocks', 'forex'],
      submissionDate: '2024-01-15',
      approvalDate: '2024-01-16'
    },
    {
      id: 2,
      name: 'Healthcare Records Dataset',
      description: 'Anonymized healthcare records for medical AI training with privacy compliance',
      category: 'healthcare',
      price: '750 XRP',
      size: '1.8 GB',
      quality: 88,
      status: 'pending',
      submitter: '0x2345...6789',
      purchaseCount: 0,
      rating: 0,
      tags: ['medical', 'anonymized', 'HIPAA', 'training'],
      submissionDate: '2024-01-20',
      approvalDate: null
    },
    {
      id: 3,
      name: 'Smart Contract Templates',
      description: 'Collection of verified smart contract templates for various DeFi protocols',
      category: 'development',
      price: '300 XRP',
      size: '500 MB',
      quality: 92,
      status: 'approved',
      submitter: '0x3456...7890',
      purchaseCount: 89,
      rating: 4.6,
      tags: ['solidity', 'defi', 'templates', 'verified'],
      submissionDate: '2024-01-10',
      approvalDate: '2024-01-12'
    },
    {
      id: 4,
      name: 'NFT Metadata Collection',
      description: 'Curated NFT metadata with attributes, rarity scores, and market data',
      category: 'nft',
      price: '200 XRP',
      size: '800 MB',
      quality: 85,
      status: 'approved',
      submitter: '0x4567...8901',
      purchaseCount: 156,
      rating: 4.4,
      tags: ['nft', 'metadata', 'rarity', 'attributes'],
      submissionDate: '2024-01-08',
      approvalDate: '2024-01-09'
    },
    {
      id: 5,
      name: 'DeFi Protocol Analytics',
      description: 'Historical data from major DeFi protocols including TVL, volume, and yield metrics',
      category: 'defi',
      price: '400 XRP',
      size: '1.2 GB',
      quality: 90,
      status: 'approved',
      submitter: '0x5678...9012',
      purchaseCount: 73,
      rating: 4.7,
      tags: ['defi', 'analytics', 'TVL', 'yield'],
      submissionDate: '2024-01-12',
      approvalDate: '2024-01-14'
    }
  ]

  const filteredDatasets = datasets.filter(dataset => {
    const matchesSearch = dataset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         dataset.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         dataset.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesCategory = selectedCategory === 'all' || dataset.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-600" />
      case 'rejected':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'rejected':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dataset Catalog</h1>
          <p className="text-gray-600">Browse and purchase Ripple-approved AI datasets</p>
        </div>
        <button className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>Submit Dataset</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search datasets by name, description, or tags..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div className="flex gap-4">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
              <option value="quality">Quality Score</option>
              <option value="popular">Most Popular</option>
            </select>
          </div>
        </div>
      </div>

      {/* Dataset Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDatasets.map((dataset) => (
          <div key={dataset.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{dataset.name}</h3>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{dataset.description}</p>
                </div>
                <div className="flex items-center space-x-1 ml-2">
                  {getStatusIcon(dataset.status)}
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Category</span>
                  <span className="text-sm font-medium text-gray-900 capitalize">{dataset.category}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Price</span>
                  <span className="text-lg font-bold text-primary-600">{dataset.price}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Size</span>
                  <span className="text-sm font-medium text-gray-900">{dataset.size}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Quality Score</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full" 
                        style={{ width: `${dataset.quality}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900">{dataset.quality}%</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Status</span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(dataset.status)}`}>
                    {dataset.status.charAt(0).toUpperCase() + dataset.status.slice(1)}
                  </span>
                </div>

                {dataset.rating > 0 && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Rating</span>
                    <div className="flex items-center space-x-1">
                      <Star className="h-4 w-4 text-yellow-400 fill-current" />
                      <span className="text-sm font-medium text-gray-900">{dataset.rating}</span>
                      <span className="text-sm text-gray-500">({dataset.purchaseCount} purchases)</span>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-4 flex flex-wrap gap-1">
                {dataset.tags.map((tag, index) => (
                  <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                    {tag}
                  </span>
                ))}
              </div>

              <div className="mt-6 flex space-x-3">
                <button className="flex-1 bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 flex items-center justify-center space-x-2">
                  <Download className="h-4 w-4" />
                  <span>Purchase</span>
                </button>
                <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center justify-center">
                  <Eye className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredDatasets.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Search className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No datasets found</h3>
          <p className="text-gray-600">Try adjusting your search criteria or browse all categories</p>
        </div>
      )}
    </div>
  )
}

export default DatasetCatalog
