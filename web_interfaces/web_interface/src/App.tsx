import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Trading from './pages/Trading'
import DeFi from './pages/DeFi'
import NFTs from './pages/NFTs'
import Portfolio from './pages/Portfolio'
import Settings from './pages/Settings'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/trading" element={<Trading />} />
          <Route path="/defi" element={<DeFi />} />
          <Route path="/nfts" element={<NFTs />} />
          <Route path="/portfolio" element={<Portfolio />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
