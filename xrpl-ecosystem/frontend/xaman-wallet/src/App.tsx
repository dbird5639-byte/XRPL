import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useWalletStore } from './stores/walletStore'
import { useXRPLStore } from './stores/xrplStore'
import Layout from './components/Layout'
import Home from './pages/Home'
import Wallet from './pages/Wallet'
import DeFi from './pages/DeFi'
import Trading from './pages/Trading'
import NFTs from './pages/NFTs'
import Settings from './pages/Settings'
import ConnectWallet from './pages/ConnectWallet'
import LoadingScreen from './components/LoadingScreen'

function App() {
  const { isConnected, isLoading } = useWalletStore()
  const { isInitialized } = useXRPLStore()

  // Show loading screen while initializing
  if (isLoading || !isInitialized) {
    return <LoadingScreen />
  }

  // Redirect to connect wallet if not connected
  if (!isConnected) {
    return <ConnectWallet />
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/wallet" element={<Wallet />} />
        <Route path="/defi" element={<DeFi />} />
        <Route path="/trading" element={<Trading />} />
        <Route path="/nfts" element={<NFTs />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}

export default App
