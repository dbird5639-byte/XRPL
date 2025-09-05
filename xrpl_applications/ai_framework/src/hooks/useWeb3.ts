import { useState, useEffect, useCallback } from 'react'
import { web3Service, WalletInfo } from '../services/web3Service'

export interface UseWeb3Return {
  wallet: WalletInfo | null
  isConnected: boolean
  isLoading: boolean
  error: string | null
  connect: () => Promise<void>
  disconnect: () => void
  switchNetwork: () => Promise<void>
  refreshBalance: () => Promise<void>
}

export const useWeb3 = (): UseWeb3Return => {
  const [wallet, setWallet] = useState<WalletInfo | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Check if wallet is already connected on mount
  useEffect(() => {
    const checkConnection = async () => {
      if (web3Service.isConnected()) {
        try {
          const walletInfo = await web3Service.getWalletInfo()
          if (walletInfo) {
            setWallet(walletInfo)
            setIsConnected(true)
          }
        } catch (err) {
          console.error('Failed to get wallet info:', err)
        }
      }
    }

    checkConnection()
  }, [])

  // Listen for account changes
  useEffect(() => {
    const handleAccountsChanged = (accounts: string[]) => {
      if (accounts.length === 0) {
        // User disconnected
        setWallet(null)
        setIsConnected(false)
      } else {
        // Account changed, refresh wallet info
        refreshBalance()
      }
    }

    const handleChainChanged = () => {
      // Chain changed, refresh wallet info
      refreshBalance()
    }

    if (window.ethereum) {
      window.ethereum.on('accountsChanged', handleAccountsChanged)
      window.ethereum.on('chainChanged', handleChainChanged)

      return () => {
        window.ethereum.removeListener('accountsChanged', handleAccountsChanged)
        window.ethereum.removeListener('chainChanged', handleChainChanged)
      }
    }
  }, [])

  const connect = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const walletInfo = await web3Service.connectWallet()
      setWallet(walletInfo)
      setIsConnected(true)
    } catch (err: any) {
      setError(err.message || 'Failed to connect wallet')
      console.error('Wallet connection error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const disconnect = useCallback(() => {
    web3Service.disconnectWallet()
    setWallet(null)
    setIsConnected(false)
    setError(null)
  }, [])

  const switchNetwork = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      await web3Service.switchNetwork()
      // Refresh wallet info after network switch
      await refreshBalance()
    } catch (err: any) {
      setError(err.message || 'Failed to switch network')
      console.error('Network switch error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const refreshBalance = useCallback(async () => {
    try {
      const walletInfo = await web3Service.getWalletInfo()
      if (walletInfo) {
        setWallet(walletInfo)
        setIsConnected(true)
      }
    } catch (err) {
      console.error('Failed to refresh balance:', err)
    }
  }, [])

  return {
    wallet,
    isConnected,
    isLoading,
    error,
    connect,
    disconnect,
    switchNetwork,
    refreshBalance
  }
}
