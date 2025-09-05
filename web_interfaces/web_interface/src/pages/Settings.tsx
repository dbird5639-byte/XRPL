import React, { useState } from 'react'
import { User, Bell, Shield, Palette, Globe, Key, Trash2 } from 'lucide-react'

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState('profile')
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    sms: false,
    trading: true,
    security: true
  })

  const settingsTabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'appearance', name: 'Appearance', icon: Palette },
    { id: 'language', name: 'Language', icon: Globe },
    { id: 'api', name: 'API Keys', icon: Key },
    { id: 'danger', name: 'Danger Zone', icon: Trash2 }
  ]

  const handleNotificationChange = (key: string, value: boolean) => {
    setNotifications(prev => ({ ...prev, [key]: value }))
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Manage your account and preferences</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="flex">
          {/* Sidebar */}
          <div className="w-64 border-r border-gray-200">
            <nav className="p-4">
              {settingsTabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md mb-1 ${
                    activeTab === tab.id
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <tab.icon className="mr-3 h-4 w-4" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1 p-6">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-gray-900">Profile Settings</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      defaultValue="John"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      defaultValue="Doe"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      defaultValue="john.doe@example.com"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone
                    </label>
                    <input
                      type="tel"
                      defaultValue="+1 (555) 123-4567"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                </div>
                
                <button className="px-4 py-2 bg-primary-600 text-white font-medium rounded-md hover:bg-primary-700 transition-colors">
                  Save Changes
                </button>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-gray-900">Notification Preferences</h2>
                
                <div className="space-y-4">
                  {Object.entries(notifications).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900 capitalize">
                          {key.replace('_', ' ')}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {key === 'email' && 'Receive notifications via email'}
                          {key === 'push' && 'Receive push notifications'}
                          {key === 'sms' && 'Receive SMS notifications'}
                          {key === 'trading' && 'Get notified about trading activities'}
                          {key === 'security' && 'Get notified about security events'}
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={value}
                          onChange={(e) => handleNotificationChange(key, e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-gray-900">Security Settings</h2>
                
                <div className="space-y-4">
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-900 mb-2">Two-Factor Authentication</h3>
                    <p className="text-sm text-gray-500 mb-3">Add an extra layer of security to your account</p>
                    <button className="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-md hover:bg-primary-700 transition-colors">
                      Enable 2FA
                    </button>
                  </div>
                  
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-900 mb-2">Change Password</h3>
                    <p className="text-sm text-gray-500 mb-3">Update your account password</p>
                    <button className="px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700 transition-colors">
                      Change Password
                    </button>
                  </div>
                  
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-900 mb-2">API Keys</h3>
                    <p className="text-sm text-gray-500 mb-3">Manage your API keys for trading</p>
                    <button className="px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700 transition-colors">
                      Manage API Keys
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'appearance' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-gray-900">Appearance</h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Theme
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                      <option>Light</option>
                      <option>Dark</option>
                      <option>System</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Language
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                      <option>English</option>
                      <option>Spanish</option>
                      <option>French</option>
                      <option>German</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Currency
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                      <option>USD</option>
                      <option>EUR</option>
                      <option>GBP</option>
                      <option>JPY</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'language' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-gray-900">Language & Region</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Language
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                      <option>English (US)</option>
                      <option>English (UK)</option>
                      <option>Spanish</option>
                      <option>French</option>
                      <option>German</option>
                      <option>Chinese</option>
                      <option>Japanese</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Timezone
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                      <option>UTC-8 (Pacific)</option>
                      <option>UTC-5 (Eastern)</option>
                      <option>UTC+0 (GMT)</option>
                      <option>UTC+1 (CET)</option>
                      <option>UTC+8 (CST)</option>
                      <option>UTC+9 (JST)</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'api' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-gray-900">API Keys</h2>
                
                <div className="p-4 border border-gray-200 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Trading API</h3>
                  <p className="text-sm text-gray-500 mb-3">Generate API keys for automated trading</p>
                  <button className="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-md hover:bg-primary-700 transition-colors">
                    Generate New Key
                  </button>
                </div>
                
                <div className="p-4 border border-gray-200 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Read-Only API</h3>
                  <p className="text-sm text-gray-500 mb-3">Generate read-only API keys for data access</p>
                  <button className="px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700 transition-colors">
                    Generate Read-Only Key
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'danger' && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-gray-900">Danger Zone</h2>
                
                <div className="p-4 border border-red-200 rounded-lg bg-red-50">
                  <h3 className="text-sm font-medium text-red-900 mb-2">Delete Account</h3>
                  <p className="text-sm text-red-700 mb-3">
                    Permanently delete your account and all associated data. This action cannot be undone.
                  </p>
                  <button className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700 transition-colors">
                    Delete Account
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
