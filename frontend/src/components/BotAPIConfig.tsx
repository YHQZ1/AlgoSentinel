import { useState } from 'react'
import { Plus, Trash2, Check, AlertCircle } from 'lucide-react'
import { apiClient } from '../api/client'

interface BotAPIStatus {
  bot_id: string
  exchange: string
  testnet: boolean
  connected_at: string
  connected: boolean
  status: string
}

const EXCHANGES = ['binance', 'coinbase', 'kraken', 'bitfinex', 'huobi']

export default function BotAPIConfig() {
  const [botId, setBotId] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [apiSecret, setApiSecret] = useState('')
  const [exchange, setExchange] = useState('binance')
  const [testnet, setTestnet] = useState(true)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)
  const [botStatuses, setBotStatuses] = useState<BotAPIStatus[]>([])

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!botId || !apiKey || !apiSecret) {
      setMessage({ type: 'error', text: 'All fields are required' })
      return
    }

    setLoading(true)
    try {
      const response = await apiClient.configureBotAPI({
        bot_id: botId,
        api_key: apiKey,
        api_secret: apiSecret,
        exchange,
        testnet
      })
      setMessage({ type: 'success', text: response.data.message })
      
      // Fetch status
      const status = await apiClient.getBotAPIStatus(botId)
      setBotStatuses([...botStatuses, status.data])
      
      // Reset form
      setBotId('')
      setApiKey('')
      setApiSecret('')
      setExchange('binance')
      setTestnet(true)
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to configure bot API'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDisconnect = async (id: string) => {
    setLoading(true)
    try {
      await apiClient.disconnectBotAPI(id)
      setBotStatuses(botStatuses.filter(b => b.bot_id !== id))
      setMessage({ type: 'success', text: `Bot ${id} disconnected` })
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to disconnect bot'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-neon-blue mb-2">Trading Bot API Configuration</h2>
        <p className="text-slate-400 text-sm">Connect your trading bot for real-time risk monitoring</p>
      </div>

      {message && (
        <div className={`p-4 rounded-lg glass border-l-4 ${
          message.type === 'success'
            ? 'border-neon-green bg-neon-green/5'
            : 'border-neon-red bg-neon-red/5'
        }`}>
          <p className={message.type === 'success' ? 'text-neon-green' : 'text-neon-red'}>
            {message.text}
          </p>
        </div>
      )}

      {/* Configuration Form */}
      <form onSubmit={handleConnect} className="glass rounded-lg p-6 space-y-4">
        <h3 className="font-bold text-neon-blue mb-4 flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Add New Trading Bot
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Bot ID</label>
            <input
              type="text"
              value={botId}
              onChange={(e) => setBotId(e.target.value)}
              placeholder="my-trading-bot-1"
              className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-neon-blue transition-colors"
              disabled={loading}
            />
            <p className="text-xs text-slate-500 mt-1">Unique identifier for your bot</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Exchange</label>
            <select
              value={exchange}
              onChange={(e) => setExchange(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-100 focus:outline-none focus:border-neon-blue transition-colors"
              disabled={loading}
            >
              {EXCHANGES.map(ex => (
                <option key={ex} value={ex}>{ex.toUpperCase()}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">API Key</label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="••••••••••••••••"
              className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-neon-blue transition-colors"
              disabled={loading}
            />
            <p className="text-xs text-slate-500 mt-1">Your API credentials are secure</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">API Secret</label>
            <input
              type="password"
              value={apiSecret}
              onChange={(e) => setApiSecret(e.target.value)}
              placeholder="••••••••••••••••"
              className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-neon-blue transition-colors"
              disabled={loading}
            />
          </div>

          <div className="col-span-1 md:col-span-2">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={testnet}
                onChange={(e) => setTestnet(e.target.checked)}
                className="w-4 h-4 rounded"
                disabled={loading}
              />
              <span className="text-sm text-slate-300">Use Testnet (Recommended for testing)</span>
            </label>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full px-6 py-3 bg-gradient-to-r from-neon-blue to-neon-purple rounded-lg font-bold text-slate-900 hover:shadow-lg hover:shadow-neon-blue/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-slate-900 border-t-neon-blue rounded-full animate-spin"></div>
              Connecting...
            </>
          ) : (
            <>
              <Plus className="w-5 h-5" />
              Connect Bot
            </>
          )}
        </button>
      </form>

      {/* Connected Bots */}
      {botStatuses.length > 0 && (
        <div className="space-y-3">
          <h3 className="font-bold text-neon-blue mb-4">Connected Bots</h3>
          {botStatuses.map((bot) => (
            <div key={bot.bot_id} className="glass rounded-lg p-4 flex items-center justify-between hover:shadow-lg transition-all duration-300">
              <div className="flex items-center gap-4">
                <div className={`w-3 h-3 rounded-full ${bot.connected ? 'bg-neon-green animate-pulse' : 'bg-neon-red'}`}></div>
                <div>
                  <p className="font-bold text-slate-100">{bot.bot_id}</p>
                  <p className="text-sm text-slate-400">
                    {bot.exchange.toUpperCase()} {bot.testnet ? '(Testnet)' : '(Mainnet)'} • Connected {new Date(bot.connected_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleDisconnect(bot.bot_id)}
                disabled={loading}
                className="p-2 text-neon-red hover:bg-neon-red/20 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass rounded-lg p-6 border-l-4 border-neon-blue">
          <h4 className="font-bold text-neon-blue mb-2 flex items-center gap-2">
            <Check className="w-5 h-5" />
            Secure Connection
          </h4>
          <p className="text-sm text-slate-400">
            API credentials are stored temporarily in Redis and expire automatically. Use read-only keys for monitoring.
          </p>
        </div>

        <div className="glass rounded-lg p-6 border-l-4 border-neon-purple">
          <h4 className="font-bold text-neon-purple mb-2 flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            Real-time Monitoring
          </h4>
          <p className="text-sm text-slate-400">
            Once connected, AlgoSentinel will automatically monitor your bot's behavior and trigger protective measures if anomalies are detected.
          </p>
        </div>
      </div>

      {/* Setup Guide */}
      <div className="glass rounded-lg p-6">
        <h3 className="font-bold text-neon-blue mb-4">📚 Setup Guide</h3>
        <ol className="space-y-3 text-sm text-slate-300">
          <li className="flex gap-3">
            <span className="font-bold text-neon-blue flex-shrink-0">1.</span>
            <span>Create an API key on your exchange account with read-only permissions</span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-neon-blue flex-shrink-0">2.</span>
            <span>Copy your API key and secret and paste them here</span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-neon-blue flex-shrink-0">3.</span>
            <span>Choose the correct exchange and enable testnet for initial testing</span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-neon-blue flex-shrink-0">4.</span>
            <span>Click "Connect Bot" to start real-time monitoring</span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-neon-blue flex-shrink-0">5.</span>
            <span>Your bot's telemetry will now appear in the Dashboard</span>
          </li>
        </ol>
      </div>
    </div>
  )
}
