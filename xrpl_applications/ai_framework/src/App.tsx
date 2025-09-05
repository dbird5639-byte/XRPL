import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import DatasetCatalog from './pages/DatasetCatalog'
import AgentBuilder from './pages/AgentBuilder'
import AutomationStudio from './pages/AutomationStudio'
import Marketplace from './pages/Marketplace'
import Settings from './pages/Settings'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/datasets" element={<DatasetCatalog />} />
          <Route path="/agents" element={<AgentBuilder />} />
          <Route path="/automation" element={<AutomationStudio />} />
          <Route path="/marketplace" element={<Marketplace />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
