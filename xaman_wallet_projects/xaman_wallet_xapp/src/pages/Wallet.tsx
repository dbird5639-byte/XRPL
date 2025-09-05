import React, { useState } from 'react'
import { Send, Download, Eye, EyeOff, Copy, QrCode } from 'lucide-react'
import { useWalletStore } from '../stores/walletStore'
import { useXRPLStore } from '../stores/xrplStore'
import { useQuery } from '@tanstack/react-query'
import toast from 'react-hot-toast'

const Wallet: React.FC = () => {
  const { address, balance, wallet } = useWalletStore()
  const { getAccountInfo } = useXRPLStore()
  const [showPrivateKey, setShowPrivateKey] = useState(false)
  const [showQR, setShowQR] = useState(false)

  // Fetch account info
  const { data: accountInfo, isLoading } = useQuery({
    queryKey: ['accountInfo', address],
    queryFn: () => address ? getAccountInfo(address) : null,
    enabled: !!address,
    refetchInterval: 30000,
  })

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text)
    toast.success(`${label} copied to clipboard`)
  }

  const exportWallet = () => {
    if (!wallet) return
    
    const walletData = {
      address: wallet.address,
      publicKey: wallet.publicKey,
      seed: wallet.seed,
    }
    
    const dataStr = JSON.stringify(walletData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `xaman-wallet-${address?.slice(0, 8)}.json`
    link.click()
    
    URL.revokeObjectURL(url)
    toast.success('Wallet exported successfully')
  }

  return (
    <div className="space-y-6">
      {/* Balance Card */}
      <div className="card-elevated">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-secondary-900">Wallet Balance</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowQR(!showQR)}
              className="btn-ghost p-2"
            >
              <QrCode className="w-5 h-5" />
            </button>
            <button
              onClick={exportWallet}
              className="btn-ghost p-2"
            >
              <Download className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="text-center">
          <div className="text-4xl font-bold text-secondary-900 mb-2">
            {balance ? `${parseFloat(balance).toFixed(2)}` : '0.00'} XRP
          </div>
          <p className="text-secondary-600 mb-6">
            ≈ ${balance ? (parseFloat(balance) * 0.52).toFixed(2) : '0.00'} USD
          </p>

          {/* QR Code */}
          {showQR && address && (
            <div className="bg-white p-4 rounded-lg border border-secondary-200 inline-block mb-6">
              <div className="w-48 h-48 bg-secondary-100 rounded-lg flex items-center justify-center">
                <QrCode className="w-24 h-24 text-secondary-400" />
              </div>
              <p className="text-xs text-secondary-500 mt-2">Scan to receive XRP</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-4 justify-center">
            <button className="btn-primary">
              <Send className="w-4 h-4 mr-2" />
              Send
            </button>
            <button className="btn-outline">
              <Download className="w-4 h-4 mr-2" />
              Receive
            </button>
          </div>
        </div>
      </div>

      {/* Wallet Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Address Information */}
        <div className="card">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Address Information</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Wallet Address
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={address || ''}
                  readOnly
                  className="input flex-1 font-mono text-sm"
                />
                <button
                  onClick={() => address && copyToClipboard(address, 'Address')}
                  className="btn-ghost p-2"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Public Key
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={wallet?.publicKey || ''}
                  readOnly
                  className="input flex-1 font-mono text-sm"
                />
                <button
                  onClick={() => wallet?.publicKey && copyToClipboard(wallet.publicKey, 'Public Key')}
                  className="btn-ghost p-2"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Seed Phrase
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type={showPrivateKey ? 'text' : 'password'}
                  value={wallet?.seed || ''}
                  readOnly
                  className="input flex-1 font-mono text-sm"
                />
                <button
                  onClick={() => setShowPrivateKey(!showPrivateKey)}
                  className="btn-ghost p-2"
                >
                  {showPrivateKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
                <button
                  onClick={() => wallet?.seed && copyToClipboard(wallet.seed, 'Seed Phrase')}
                  className="btn-ghost p-2"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Account Information */}
        <div className="card">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Account Information</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center py-2 border-b border-secondary-200">
              <span className="text-secondary-600">Sequence Number</span>
              <span className="font-mono text-sm">
                {accountInfo?.Sequence || 'Loading...'}
              </span>
            </div>
            
            <div className="flex justify-between items-center py-2 border-b border-secondary-200">
              <span className="text-secondary-600">Account Flags</span>
              <span className="font-mono text-sm">
                {accountInfo?.Flags || '0'}
              </span>
            </div>
            
            <div className="flex justify-between items-center py-2 border-b border-secondary-200">
              <span className="text-secondary-600">Owner Count</span>
              <span className="font-mono text-sm">
                {accountInfo?.OwnerCount || '0'}
              </span>
            </div>
            
            <div className="flex justify-between items-center py-2 border-b border-secondary-200">
              <span className="text-secondary-600">Ledger Index</span>
              <span className="font-mono text-sm">
                {accountInfo?.LedgerEntryType || 'N/A'}
              </span>
            </div>
            
            <div className="flex justify-between items-center py-2">
              <span className="text-secondary-600">Account Root</span>
              <span className="font-mono text-sm">
                {accountInfo?.index || 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Security Warning */}
      <div className="card bg-warning-50 border-warning-200">
        <div className="flex items-start space-x-3">
          <div className="p-2 bg-warning-100 rounded-lg">
            <Eye className="w-5 h-5 text-warning-600" />
          </div>
          <div>
            <h3 className="text-sm font-medium text-warning-800">Security Notice</h3>
            <p className="text-sm text-warning-700 mt-1">
              Never share your seed phrase or private keys with anyone. xAman Wallet cannot recover your funds if you lose access to your wallet.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Wallet
