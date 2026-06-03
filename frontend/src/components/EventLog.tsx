import { useEffect, useState } from 'react'
import { AlertCircle, CheckCircle, Zap, AlertTriangle } from 'lucide-react'
import { apiClient } from '../api/client'

interface Event {
  timestamp?: string
  event_type: string
  message: string
  action?: string
  humanized: string
  session_id: string
}

export default function EventLog() {
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchEvents = async () => {
      setLoading(true)
      try {
        const response = await apiClient.getEvents(50)
        setEvents(response.data)
        setError(null)
      } catch (err) {
        setError('Failed to fetch events')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchEvents()
    const interval = setInterval(fetchEvents, 3000)
    return () => clearInterval(interval)
  }, [])

  const getEventIcon = (event: Event) => {
    if (event.action === 'KILL_SURE') {
      return <AlertTriangle className="w-5 h-5 text-neon-red" />
    }
    if (event.event_type === 'CALIBRATION_COMPLETE') {
      return <CheckCircle className="w-5 h-5 text-neon-green" />
    }
    if (event.event_type === 'ANOMALY_ACTION') {
      return <Zap className="w-5 h-5 text-yellow-400" />
    }
    return <AlertCircle className="w-5 h-5 text-neon-blue" />
  }

  const getEventColor = (event: Event) => {
    if (event.action === 'KILL_SURE') return 'border-neon-red'
    if (event.event_type === 'CALIBRATION_COMPLETE') return 'border-neon-green'
    if (event.event_type === 'ANOMALY_ACTION') return 'border-yellow-400'
    return 'border-neon-blue'
  }

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

  if (loading && events.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block mb-4">
            <div className="w-12 h-12 border-2 border-neon-blue border-t-neon-purple rounded-full animate-spin"></div>
          </div>
          <p className="text-slate-400">Loading events...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-neon-blue">System Events</h2>
        <span className="text-sm text-slate-400">{events.length} events</span>
      </div>

      {events.length === 0 ? (
        <div className="glass rounded-lg p-8 text-center">
          <p className="text-slate-400">No events yet. Waiting for system activity...</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-screen overflow-y-auto pr-2">
          {events.map((event, index) => (
            <div
              key={index}
              className={`glass rounded-lg p-4 border-l-4 ${getEventColor(event)} hover:shadow-lg transition-all duration-300 hover:shadow-neon-blue/20`}
            >
              <div className="flex items-start gap-4">
                <div className="mt-1 flex-shrink-0">
                  {getEventIcon(event)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-bold text-slate-100 text-sm">{event.event_type}</h3>
                    {event.timestamp && (
                      <span className="text-xs text-slate-500">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-slate-300 mb-2">{event.humanized}</p>
                  <div className="flex flex-wrap gap-2">
                    {event.action && (
                      <span className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-300">
                        Action: {event.action}
                      </span>
                    )}
                    <span className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-400 font-mono">
                      {event.session_id.slice(0, 8)}...
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
