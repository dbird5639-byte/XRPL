import React from 'react'
import { Settings as SettingsIcon, Shield, Globe, Bell, Palette } from 'lucide-react'

const Settings: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-secondary-900">Settings</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Network</h3>
          <div className="space-y-3">
            <label className="flex items-center">
              <input type="radio" name="network" value="testnet" defaultChecked className="mr-3" />
              <span>Testnet</span>
            </label>
            <label className="flex items-center">
              <input type="radio" name="network" value="mainnet" className="mr-3" />
              <span>Mainnet</span>
            </label>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Security</h3>
          <div className="space-y-3">
            <button className="btn-outline w-full">Change Password</button>
            <button className="btn-outline w-full">Export Wallet</button>
            <button className="btn-error w-full">Delete Wallet</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
