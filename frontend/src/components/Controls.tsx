import { useState } from 'react'
import { Zap, AlertTriangle, RotateCcw, Loader } from 'lucide-react'
import { apiClient } from '../api/client'

export default function Controls() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  const executeCommand = async (command: string) => {
    setLoading(true)
    try {
      const response = await apiClient.sendCommand(command)
      setMessage({
        type: 'success',
        text: response.data.message
      })
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to execute command'
      })
    } finally {
      setLoading(false)
    }
  }

  const CommandButton = ({ icon: Icon, label, description, onClick, danger = false }: any) => (
    <button
      onClick={onClick}
      disabled={loading}
      className={`glass rounded-lg p-6 flex items-center gap-4 hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed group ${
        danger
          ? 'hover:shadow-neon-red/30 hover:border-neon-red'
          : 'hover:shadow-neon-blue/30 hover:border-neon-blue'
      }`}
    >
      <div className={`p-3 rounded-lg ${
        danger
          ? 'bg-neon-red/20 group-hover:bg-neon-red/30'
          : 'bg-neon-blue/20 group-hover:bg-neon-blue/30'
      }`}>
        <Icon className={`w-6 h-6 ${danger ? 'text-neon-red' : 'text-neon-blue'}`} />
      </div>
      <div className="text-left">
        <h3 className="font-bold text-slate-100">{label}</h3>
        <p className="text-sm text-slate-400">{description}</p>
      </div>
      {loading && <Loader className="w-4 h-4 animate-spin ml-auto text-slate-400" />}
    </button>
  )

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-neon-blue mb-2">System Controls</h2>
        <p className="text-slate-400 text-sm">Manage bot behavior and risk parameters</p>
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

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Trigger Rogue Mode */}
        <CommandButton
          icon={Zap}
          label="Trigger Rogue Mode"
          description="Force bot into anomalous state for testing"
          onClick={() => executeCommand('FORCE_ROGUE')}
          danger={false}
        />

        {/* Kill Switch */}
        <CommandButton
          icon={AlertTriangle}
          label="Manual Kill Switch"
          description="Immediately halt all trading operations"
          onClick={() => executeCommand('KILL_SURE')}
          danger={true}
        />

        {/* Reset Bot */}
        <CommandButton
          icon={RotateCcw}
          label="Reset Bot"
          description="Return system to healthy baseline state"
          onClick={() => executeCommand('RESET_BOT')}
          danger={false}
        />
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="glass rounded-lg p-6 border-l-4 border-neon-blue">
          <h3 className="font-bold text-neon-blue mb-2">🚨 Rogue Mode</h3>
          <p className="text-sm text-slate-400">
            Tests the Sentinel's ability to detect abnormal behavior patterns
          </p>
        </div>

        <div className="glass rounded-lg p-6 border-l-4 border-neon-red">
          <h3 className="font-bold text-neon-red mb-2">🛑 Kill Switch</h3>
          <p className="text-sm text-slate-400">
            Emergency stop - flattens positions and halts all trading immediately
          </p>
        </div>

        <div className="glass rounded-lg p-6 border-l-4 border-neon-green">
          <h3 className="font-bold text-neon-green mb-2">♻️ Reset</h3>
          <p className="text-sm text-slate-400">
            Returns the bot to its initial healthy operating state with fresh calibration
          </p>
        </div>
      </div>

      {/* Additional Control Panel */}
      <div className="glass rounded-lg p-6">
        <h3 className="font-bold text-neon-blue mb-4">Advanced Options</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-slate-800 bg-opacity-50 rounded">
            <span className="text-slate-300">Auto-calibration</span>
            <input type="checkbox" className="w-4 h-4" defaultChecked disabled />
          </div>
          <div className="flex items-center justify-between p-3 bg-slate-800 bg-opacity-50 rounded">
            <span className="text-slate-300">Real-time anomaly detection</span>
            <input type="checkbox" className="w-4 h-4" defaultChecked disabled />
          </div>
          <div className="flex items-center justify-between p-3 bg-slate-800 bg-opacity-50 rounded">
            <span className="text-slate-300">Emergency protocols enabled</span>
            <input type="checkbox" className="w-4 h-4" defaultChecked disabled />
          </div>
        </div>
      </div>
    </div>
  )
}
