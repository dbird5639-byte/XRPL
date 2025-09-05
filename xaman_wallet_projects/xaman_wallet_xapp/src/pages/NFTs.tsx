import React from 'react'
import { Image, Plus, Filter } from 'lucide-react'

const NFTs: React.FC = () => {
  const nfts = [
    { id: 1, name: 'XRPL Art #1', image: '/api/placeholder/200/200', price: '10 XRP' },
    { id: 2, name: 'XRPL Art #2', image: '/api/placeholder/200/200', price: '15 XRP' },
    { id: 3, name: 'XRPL Art #3', image: '/api/placeholder/200/200', price: '8 XRP' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-secondary-900">NFT Collection</h1>
        <div className="flex space-x-2">
          <button className="btn-outline">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </button>
          <button className="btn-primary">
            <Plus className="w-4 h-4 mr-2" />
            Mint NFT
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {nfts.map((nft) => (
          <div key={nft.id} className="card">
            <div className="aspect-square bg-secondary-100 rounded-lg mb-4 flex items-center justify-center">
              <Image className="w-16 h-16 text-secondary-400" />
            </div>
            <h3 className="font-medium text-secondary-900 mb-2">{nft.name}</h3>
            <p className="text-sm text-secondary-600 mb-4">{nft.price}</p>
            <button className="btn-primary w-full">View Details</button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default NFTs
