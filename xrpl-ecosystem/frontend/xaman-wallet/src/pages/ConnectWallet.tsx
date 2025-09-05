import React, { useState } from 'react'
import { Wallet, Zap, Shield, Globe } from 'lucide-react'
import { useWalletStore } from '../stores/walletStore'
import { useXRPLStore } from '../stores/xrplStore'
import { Wallet as XRPLWallet } from '@xrplf/xrpl'
import toast from 'react-hot-toast'

const ConnectWallet: React.FC = () => {
  const [isConnecting, setIsConnecting] = useState(false)
  const [seedPhrase, setSeedPhrase] = useState('')
  const { connect, setLoading, setError } = useWalletStore()
  const { initialize } = useXRPLStore()

  const handleConnect = async () => {
    if (!seedPhrase.trim()) {
      toast.error('Please enter a seed phrase')
      return
    }

    setIsConnecting(true)
    setLoading(true)

    try {
      // Initialize XRPL connection
      await initialize('testnet')
      
      // Create wallet from seed phrase
      const wallet = XRPLWallet.fromSeed(seedPhrase.trim())
      
      // Connect wallet
      connect(wallet)
      
      toast.success('Wallet connected successfully!')
    } catch (error) {
      console.error('Connection error:', error)
      setError(error instanceof Error ? error.message : 'Failed to connect wallet')
      toast.error('Failed to connect wallet')
    } finally {
      setIsConnecting(false)
      setLoading(false)
    }
  }

  const generateNewWallet = async () => {
    setIsConnecting(true)
    setLoading(true)

    try {
      // Initialize XRPL connection
      await initialize('testnet')
      
      // Generate new wallet
      const wallet = XRPLWallet.generate()
      
      // Connect wallet
      connect(wallet)
      
      toast.success('New wallet created and connected!')
    } catch (error) {
      console.error('Wallet generation error:', error)
      setError(error instanceof Error ? error.message : 'Failed to generate wallet')
      toast.error('Failed to generate wallet')
    } finally {
      setIsConnecting(false)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-primary rounded-3xl flex items-center justify-center mx-auto mb-4">
            <Zap className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">xAman Wallet</h1>
          <p className="text-secondary-600">Connect to the XRP Ledger</p>
        </div>

        {/* Connection Card */}
        <div className="card-elevated">
          <div className="space-y-6">
            {/* Features */}
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-3 bg-primary-50 rounded-lg">
                <Shield className="w-6 h-6 text-primary-600 mx-auto mb-2" />
                <p className="text-xs text-primary-700 font-medium">Secure</p>
              </div>
              <div className="p-3 bg-success-50 rounded-lg">
                <Globe className="w-6 h-6 text-success-600 mx-auto mb-2" />
                <p className="text-xs text-success-700 font-medium">Global</p>
              </div>
              <div className="p-3 bg-warning-50 rounded-lg">
                <Zap className="w-6 h-6 text-warning-600 mx-auto mb-2" />
                <p className="text-xs text-warning-700 font-medium">Fast</p>
              </div>
            </div>

            {/* Seed Phrase Input */}
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Enter Seed Phrase
              </label>
              <textarea
                value={seedPhrase}
                onChange={(e) => setSeedPhrase(e.target.value)}
                placeholder="Enter your 24-word seed phrase..."
                className="input h-24 resize-none"
                disabled={isConnecting}
              />
              <p className="text-xs text-secondary-500 mt-1">
                Your seed phrase is encrypted and stored locally
              </p>
            </div>

            {/* Connect Button */}
            <button
              onClick={handleConnect}
              disabled={isConnecting || !seedPhrase.trim()}
              className="btn-primary w-full"
            >
              {isConnecting ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Connecting...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center space-x-2">
                  <Wallet className="w-4 h-4" />
                  <span>Connect Wallet</span>
                </div>
              )}
            </button>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-secondary-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-secondary-500">Or</span>
              </div>
            </div>

            {/* Generate New Wallet */}
            <button
              onClick={generateNewWallet}
              disabled={isConnecting}
              className="btn-outline w-full"
            >
              {isConnecting ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                  <span>Generating...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center space-x-2">
                  <Zap className="w-4 h-4" />
                  <span>Generate New Wallet</span>
                </div>
              )}
            </button>
          </div>
        </div>

        {/* Security Notice */}
        <div className="mt-6 p-4 bg-warning-50 border border-warning-200 rounded-lg">
          <div className="flex items-start space-x-3">
            <Shield className="w-5 h-5 text-warning-600 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-warning-800">Security Notice</h3>
              <p className="text-xs text-warning-700 mt-1">
                Never share your seed phrase with anyone. xAman Wallet cannot recover your funds if you lose your seed phrase.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ConnectWallet
