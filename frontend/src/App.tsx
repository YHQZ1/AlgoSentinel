import { useEffect, useState } from 'react'
import { Activity, AlertTriangle, Zap, Shield, Settings, Wifi, WifiOff } from 'lucide-react'
import { apiClient } from './api/client'
import Dashboard from './components/Dashboard'
import EventLog from './components/EventLog'
import Controls from './components/Controls'
import Statistics from './components/Statistics'
import BotAPIConfig from './components/BotAPIConfig'

export default function App() {
  const [isConnected, setIsConnected] = useState(false)
  const [activeTab, setActiveTab] = useState<'dashboard' | 'events' | 'controls' | 'stats' | 'bot-api'>('dashboard')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await apiClient.getHealth()
        setIsConnected(true)
      } catch (error) {
        setIsConnected(false)
      } finally {
        setLoading(false)
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="text-center">
          <div className="inline-block mb-4">
            <div className="w-16 h-16 border-4 border-neon-blue border-t-neon-purple rounded-full animate-spin"></div>
          </div>
          <h1 className="text-2xl font-bold text-neon-blue mb-2">AlgoSentinel</h1>
          <p className="text-slate-400">Initializing...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="glass border-b border-neon-blue border-opacity-20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Shield className="w-8 h-8 text-neon-blue animate-pulse" />
              <div className="absolute inset-0 bg-neon-blue opacity-20 rounded-full blur-md animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-black bg-gradient-to-r from-neon-blue to-neon-purple bg-clip-text text-transparent">
                AlgoSentinel
              </h1>
              <p className="text-xs text-slate-400">AI Risk Management System</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {isConnected ? (
              <div className="flex items-center gap-2 px-3 py-1 rounded-full glass">
                <Wifi className="w-4 h-4 text-neon-green animate-pulse" />
                <span className="text-sm text-neon-green">Connected</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 px-3 py-1 rounded-full glass">
                <WifiOff className="w-4 h-4 text-neon-red animate-pulse" />
                <span className="text-sm text-neon-red">Disconnected</span>
              </div>
            )}
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-7xl mx-auto px-6 flex gap-2 border-t border-slate-700 border-opacity-50">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: Activity },
            { id: 'events', label: 'Events', icon: AlertTriangle },
            { id: 'stats', label: 'Statistics', icon: Zap },
            { id: 'controls', label: 'Controls', icon: Shield },
            { id: 'bot-api', label: 'Bot API', icon: Settings },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`px-4 py-3 flex items-center gap-2 border-b-2 transition-all ${
                activeTab === id
                  ? 'border-neon-blue text-neon-blue'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm font-medium hidden sm:inline">{label}</span>
            </button>
          ))}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {!isConnected && (
          <div className="mb-6 p-4 rounded-lg glass border-l-4 border-neon-red">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-neon-red" />
              <div>
                <h3 className="font-bold text-neon-red">Connection Error</h3>
                <p className="text-sm text-slate-300">Unable to connect to API. Please check your connection.</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'events' && <EventLog />}
        {activeTab === 'stats' && <Statistics />}
        {activeTab === 'controls' && <Controls />}
        {activeTab === 'bot-api' && <BotAPIConfig />}
      </main>

      {/* Footer */}
      <footer className="glass border-t border-slate-700 border-opacity-50 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6 text-center text-slate-400 text-sm">
          <p>🛡️ AlgoSentinel - Protecting Your Trading Strategy • © 2024</p>
        </div>
      </footer>
    </div>
  )
}
