import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiClient = {
  // Health & Status
  getHealth: () => api.get('/health'),
  
  // Telemetry
  getTelemetry: (limit?: number) => 
    api.get('/telemetry', { params: { limit } }),
  
  // Events
  getEvents: (limit?: number) => 
    api.get('/events', { params: { limit } }),
  
  // Commands
  sendCommand: (command: string) =>
    api.post('/command', { command }),
  
  // Bot API Configuration
  configureBotAPI: (config: {
    api_key: string
    api_secret: string
    exchange: string
    testnet: boolean
    bot_id: string
  }) => api.post('/bot-api/config', config),
  
  getBotAPIStatus: (botId: string) =>
    api.get(`/bot-api/status/${botId}`),
  
  disconnectBotAPI: (botId: string) =>
    api.delete(`/bot-api/disconnect/${botId}`),
  
  // Statistics
  getStats: () => api.get('/stats'),
}

export default api
