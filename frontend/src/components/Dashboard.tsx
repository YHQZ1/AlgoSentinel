import { useEffect, useState } from 'react'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { AlertCircle } from 'lucide-react'
import { apiClient } from '../api/client'

interface Telemetry {
  trade_freq: number
  volatility: number
  order_cancel_rate: number
  latency: number
  mode: string
  session_id: string
}

export default function Dashboard() {
  const [telemetry, setTelemetry] = useState<Telemetry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchTelemetry = async () => {
      setLoading(true)
      try {
        const response = await apiClient.getTelemetry(100)
        setTelemetry(response.data)
        setError(null)
      } catch (err) {
        setError('Failed to fetch telemetry data')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchTelemetry()
    const interval = setInterval(fetchTelemetry, 3000)
    return () => clearInterval(interval)
  }, [])

  const getLatestMetrics = () => {
    if (telemetry.length === 0) return null
    return telemetry[telemetry.length - 1]
  }

  const latest = getLatestMetrics()

  const chartData = telemetry.map((t, i) => ({
    id: i,
    trade_freq: t.trade_freq,
    volatility: t.volatility,
    order_cancel_rate: t.order_cancel_rate,
    latency: t.latency,
  }))

  const MetricCard = ({ label, value, unit, trend, status }: any) => (
    <div className="glass rounded-lg p-4 hover:border-neon-purple transition-all duration-300 hover:shadow-lg hover:shadow-neon-purple/20">
      <div className="flex items-center justify-between mb-2">
        <span className="text-slate-400 text-sm">{label}</span>
        <span className={`text-xs px-2 py-1 rounded-full ${
          status === 'high' ? 'bg-neon-red/20 text-neon-red' :
          status === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
          'bg-neon-green/20 text-neon-green'
        }`}>
          {status}
        </span>
      </div>
      <div className="text-2xl font-bold text-neon-blue mb-1">
        {value.toFixed(2)} <span className="text-sm text-slate-400">{unit}</span>
      </div>
      <div className={`text-xs ${trend > 0 ? 'text-neon-red' : 'text-neon-green'}`}>
        {trend > 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(1)}%
      </div>
    </div>
  )

  if (error) {
    return (
      <div className="p-6 rounded-lg glass border-l-4 border-neon-red flex items-center gap-3">
        <AlertCircle className="w-6 h-6 text-neon-red flex-shrink-0" />
        <div>
          <h3 className="font-bold text-neon-red">Error</h3>
          <p className="text-sm text-slate-300">{error}</p>
        </div>
      </div>
    )
  }

  if (loading && telemetry.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block mb-4">
            <div className="w-12 h-12 border-2 border-neon-blue border-t-neon-purple rounded-full animate-spin"></div>
          </div>
          <p className="text-slate-400">Loading telemetry data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {latest ? (
          <>
            <MetricCard
              label="Trade Frequency"
              value={latest.trade_freq}
              unit="trades/min"
              trend={latest.trade_freq > 5 ? 15 : -5}
              status={latest.trade_freq > 10 ? 'high' : latest.trade_freq > 5 ? 'medium' : 'low'}
            />
            <MetricCard
              label="Volatility"
              value={latest.volatility}
              unit="%"
              trend={latest.volatility > 5 ? 25 : -10}
              status={latest.volatility > 10 ? 'high' : latest.volatility > 5 ? 'medium' : 'low'}
            />
            <MetricCard
              label="Order Cancel Rate"
              value={latest.order_cancel_rate}
              unit="%"
              trend={-8}
              status={latest.order_cancel_rate > 5 ? 'high' : 'low'}
            />
            <MetricCard
              label="Latency"
              value={latest.latency}
              unit="ms"
              trend={5}
              status={latest.latency > 100 ? 'high' : latest.latency > 50 ? 'medium' : 'low'}
            />
          </>
        ) : (
          <div className="col-span-4 text-center text-slate-400">No data available</div>
        )}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trade Frequency & Volatility */}
        <div className="glass rounded-lg p-6">
          <h3 className="text-lg font-bold text-neon-blue mb-4">Market Metrics</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(100, 116, 139, 0.2)" />
              <XAxis stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(15, 23, 42, 0.9)',
                  border: '1px solid rgba(0, 217, 255, 0.3)',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="trade_freq" stroke="#00d9ff" dot={false} strokeWidth={2} name="Trade Freq" />
              <Line type="monotone" dataKey="volatility" stroke="#d946ef" dot={false} strokeWidth={2} name="Volatility" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Cancel Rate & Latency */}
        <div className="glass rounded-lg p-6">
          <h3 className="text-lg font-bold text-neon-blue mb-4">Risk Indicators</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(100, 116, 139, 0.2)" />
              <XAxis stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(15, 23, 42, 0.9)',
                  border: '1px solid rgba(0, 217, 255, 0.3)',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Area type="monotone" dataKey="order_cancel_rate" fill="#22c55e" stroke="#22c55e" fillOpacity={0.3} name="Cancel Rate" />
              <Area type="monotone" dataKey="latency" fill="#ef4444" stroke="#ef4444" fillOpacity={0.3} name="Latency" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Real-time Status */}
      {latest && (
        <div className="glass rounded-lg p-6">
          <h3 className="text-lg font-bold text-neon-blue mb-4">Current Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-slate-400 text-sm mb-1">Mode</p>
              <p className={`text-lg font-bold ${latest.mode === 'HEALTHY' ? 'text-neon-green' : 'text-neon-red'}`}>
                {latest.mode}
              </p>
            </div>
            <div>
              <p className="text-slate-400 text-sm mb-1">Session ID</p>
              <p className="text-lg font-bold text-neon-blue font-mono text-sm">{latest.session_id.slice(0, 12)}...</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm mb-1">Data Points</p>
              <p className="text-lg font-bold text-neon-purple">{telemetry.length}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
