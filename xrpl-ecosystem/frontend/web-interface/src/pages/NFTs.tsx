import React, { useState } from 'react'
import { Image, Heart, Eye, Filter } from 'lucide-react'

const NFTs: React.FC = () => {
  const [activeTab, setActiveTab] = useState('marketplace')
  const [selectedCategory, setSelectedCategory] = useState('all')

  const categories = ['all', 'art', 'gaming', 'collectibles', 'music', 'sports']

  const nftItems = [
    {
      id: 1,
      name: 'Digital Art #001',
      creator: 'ArtistName',
      price: '0.5 XRP',
      image: '/api/placeholder/300/300',
      likes: 42,
      views: 128,
      category: 'art'
    },
    {
      id: 2,
      name: 'Gaming Character',
      creator: 'GameStudio',
      price: '1.2 XRP',
      image: '/api/placeholder/300/300',
      likes: 89,
      views: 256,
      category: 'gaming'
    },
    {
      id: 3,
      name: 'Rare Collectible',
      creator: 'Collector',
      price: '2.8 XRP',
      image: '/api/placeholder/300/300',
      likes: 156,
      views: 512,
      category: 'collectibles'
    },
    {
      id: 4,
      name: 'Music NFT',
      creator: 'Musician',
      price: '0.8 XRP',
      image: '/api/placeholder/300/300',
      likes: 73,
      views: 189,
      category: 'music'
    },
    {
      id: 5,
      name: 'Sports Moment',
      creator: 'SportsFan',
      price: '1.5 XRP',
      image: '/api/placeholder/300/300',
      likes: 201,
      views: 445,
      category: 'sports'
    },
    {
      id: 6,
      name: 'Abstract Art',
      creator: 'AbstractArtist',
      price: '0.3 XRP',
      image: '/api/placeholder/300/300',
      likes: 34,
      views: 98,
      category: 'art'
    }
  ]

  const filteredNFTs = selectedCategory === 'all' 
    ? nftItems 
    : nftItems.filter(nft => nft.category === selectedCategory)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">NFT Marketplace</h1>
        <p className="text-gray-600">Discover, buy, and sell unique digital assets</p>
      </div>

      {/* NFT Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {['marketplace', 'my-nfts', 'create', 'collections'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.replace('-', ' ')}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'marketplace' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <Filter className="h-5 w-5 text-gray-400" />
                  <div className="flex space-x-2">
                    {categories.map((category) => (
                      <button
                        key={category}
                        onClick={() => setSelectedCategory(category)}
                        className={`px-3 py-1 text-sm font-medium rounded-md capitalize ${
                          selectedCategory === category
                            ? 'bg-primary-100 text-primary-700'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {category}
                      </button>
                    ))}
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <select className="px-3 py-2 border border-gray-300 rounded-md text-sm">
                    <option>Price: Low to High</option>
                    <option>Price: High to Low</option>
                    <option>Recently Listed</option>
                    <option>Most Popular</option>
                  </select>
                </div>
              </div>

              {/* NFT Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {filteredNFTs.map((nft) => (
                  <div key={nft.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
                    <div className="aspect-square bg-gray-100 relative">
                      <Image className="w-full h-full object-cover" />
                      <div className="absolute top-2 right-2">
                        <button className="p-2 bg-white/80 rounded-full hover:bg-white transition-colors">
                          <Heart className="h-4 w-4 text-gray-600" />
                        </button>
                      </div>
                    </div>
                    
                    <div className="p-4">
                      <h3 className="font-semibold text-gray-900 mb-1">{nft.name}</h3>
                      <p className="text-sm text-gray-600 mb-2">by {nft.creator}</p>
                      
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-lg font-bold text-primary-600">{nft.price}</span>
                        <div className="flex items-center space-x-3 text-sm text-gray-500">
                          <div className="flex items-center">
                            <Heart className="h-4 w-4 mr-1" />
                            {nft.likes}
                          </div>
                          <div className="flex items-center">
                            <Eye className="h-4 w-4 mr-1" />
                            {nft.views}
                          </div>
                        </div>
                      </div>
                      
                      <button className="w-full py-2 bg-primary-600 text-white font-medium rounded-md hover:bg-primary-700 transition-colors">
                        Buy Now
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'my-nfts' && (
            <div className="text-center py-12">
              <Image className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No NFTs Owned</h3>
              <p className="text-gray-600">Start collecting NFTs from the marketplace</p>
            </div>
          )}

          {activeTab === 'create' && (
            <div className="max-w-2xl mx-auto">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Create New NFT</h3>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Upload Image
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <Image className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Drag and drop your image here, or click to browse</p>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    NFT Name
                  </label>
                  <input
                    type="text"
                    placeholder="Enter NFT name"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    rows={4}
                    placeholder="Describe your NFT"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Price (XRP)
                  </label>
                  <input
                    type="number"
                    placeholder="0.0"
                    step="0.1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <button className="w-full py-3 bg-primary-600 text-white font-medium rounded-md hover:bg-primary-700 transition-colors">
                  Create NFT
                </button>
              </div>
            </div>
          )}

          {activeTab === 'collections' && (
            <div className="text-center py-12">
              <Image className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Collections Coming Soon</h3>
              <p className="text-gray-600">Organize your NFTs into collections</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default NFTs
