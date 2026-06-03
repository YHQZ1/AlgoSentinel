import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { AlertCircle } from 'lucide-react'
import { apiClient } from '../api/client'

interface Stats {
  total_records: number
  total_events: number
  avg_trade_freq: number
  avg_volatility: number
  avg_latency: number
  max_trade_freq: number
  max_volatility: number
  max_latency: number
  anomaly_events: number
  kill_switch_events: number
}

export default function Statistics() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true)
      try {
        const response = await apiClient.getStats()
        setStats(response.data)
        setError(null)
      } catch (err) {
        setError('Failed to fetch statistics')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
    const interval = setInterval(fetchStats, 5000)
    return () => clearInterval(interval)
  }, [])

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

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block mb-4">
            <div className="w-12 h-12 border-2 border-neon-blue border-t-neon-purple rounded-full animate-spin"></div>
          </div>
          <p className="text-slate-400">Loading statistics...</p>
        </div>
      </div>
    )
  }

  if (!stats) return null

  const StatCard = ({ label, value, unit = '', trend = 0 }: any) => (
    <div className="glass rounded-lg p-4">
      <p className="text-slate-400 text-sm mb-2">{label}</p>
      <p className="text-2xl font-bold text-neon-blue mb-1">
        {typeof value === 'number' ? value.toFixed(2) : value} <span className="text-xs text-slate-400">{unit}</span>
      </p>
      {trend !== 0 && (
        <p className={`text-xs ${trend > 0 ? 'text-neon-red' : 'text-neon-green'}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
        </p>
      )}
    </div>
  )

  const pieData = [
    { name: 'Normal Events', value: Math.max(0, stats.total_events - stats.anomaly_events) },
    { name: 'Anomaly Events', value: stats.anomaly_events }
  ]

  const COLORS = ['#00d9ff', '#d946ef']

  const barData = [
    { name: 'Trade Freq', avg: stats.avg_trade_freq, max: stats.max_trade_freq },
    { name: 'Volatility', avg: stats.avg_volatility, max: stats.max_volatility },
    { name: 'Latency', avg: stats.avg_latency, max: stats.max_latency }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-neon-blue mb-2">System Statistics</h2>
        <p className="text-slate-400 text-sm">Aggregated metrics and performance data</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Records" value={stats.total_records} />
        <StatCard label="Total Events" value={stats.total_events} />
        <StatCard label="Anomaly Events" value={stats.anomaly_events} unit="events" />
        <StatCard label="Kill Switch Events" value={stats.kill_switch_events} unit="times" />
      </div>

      {/* Average Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard label="Avg Trade Frequency" value={stats.avg_trade_freq} unit="trades/min" />
        <StatCard label="Avg Volatility" value={stats.avg_volatility} unit="%" />
        <StatCard label="Avg Latency" value={stats.avg_latency} unit="ms" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <div className="glass rounded-lg p-6">
          <h3 className="text-lg font-bold text-neon-blue mb-4">Average vs Max Metrics</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData}>
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
              <Bar dataKey="avg" fill="#00d9ff" name="Average" />
              <Bar dataKey="max" fill="#d946ef" name="Maximum" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart */}
        <div className="glass rounded-lg p-6">
          <h3 className="text-lg font-bold text-neon-blue mb-4">Event Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
              >
                {pieData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(15, 23, 42, 0.9)',
                  border: '1px solid rgba(0, 217, 255, 0.3)',
                  borderRadius: '8px'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Summary */}
      <div className="glass rounded-lg p-6">
        <h3 className="font-bold text-neon-blue mb-4">Summary</h3>
        <div className="space-y-2 text-sm text-slate-300">
          <p>• <strong className="text-neon-blue">{stats.total_records}</strong> telemetry data points collected</p>
          <p>• <strong className="text-neon-blue">{stats.total_events}</strong> system events recorded</p>
          <p>• <strong className="text-neon-red">{stats.anomaly_events}</strong> anomalies detected</p>
          <p>• <strong className="text-neon-red">{stats.kill_switch_events}</strong> emergency stop events triggered</p>
          <p>• System uptime: <strong className="text-neon-green">Operational</strong></p>
        </div>
      </div>
    </div>
  )
}
