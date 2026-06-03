# AlgoSentinel React Frontend & API - Setup Guide

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Build and start all services
docker compose up -d

# Services will be available at:
# - Frontend: http://localhost:3000
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Legacy Streamlit Dashboard: http://localhost:8501
```

### Local Development

#### Prerequisites
- Node.js 18+
- Python 3.11+
- Redis running locally

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

Frontend will be available at `http://localhost:3000`

#### API Setup

```bash
cd api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start API server
python main.py
```

API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## 📋 Features

### Dashboard Tab
- **Real-time Telemetry**: Monitor trade frequency, volatility, order cancel rate, and latency
- **Live Charts**: Line and area charts showing market metrics and risk indicators
- **Current Status**: View bot mode (HEALTHY/ROGUE) and session information

### Events Tab
- **System Event Log**: Track all sentinel actions and bot state changes
- **Event Filtering**: Color-coded events with detailed information
- **Event Timeline**: Historical view of all system events

### Statistics Tab
- **Aggregated Metrics**: Total records, events, anomalies detected
- **Performance Analysis**: Average and maximum values for all metrics
- **Event Distribution**: Pie chart showing normal vs anomaly events
- **Bar Charts**: Comparative analysis of metrics

### Controls Tab
- **Trigger Rogue Mode**: Force bot into anomalous state for testing
- **Manual Kill Switch**: Emergency stop - halts all trading immediately
- **Reset Bot**: Return system to healthy baseline state

### Bot API Tab (NEW!)
- **Configure Trading Bot**: Connect real trading bot APIs
- **Supported Exchanges**: Binance, Coinbase, Kraken, Bitfinex, Huobi
- **Testnet Support**: Safe testing before mainnet deployment
- **Real-time Monitoring**: Automatic risk monitoring of connected bots

## 🔗 API Endpoints

### Health & Status
```
GET /health
- Returns API and Redis connection status
```

### Telemetry
```
GET /telemetry?limit=300
- Returns recent telemetry data
- Parameters: limit (default: 300)
```

### Events
```
GET /events?limit=50
- Returns system events with humanized descriptions
- Parameters: limit (default: 50)
```

### Commands
```
POST /command
- Send commands to the bot
- Body: { "command": "FORCE_ROGUE" | "KILL_SURE" | "RESET_BOT" }
```

### Bot API Configuration
```
POST /bot-api/config
- Configure a trading bot API connection
- Body: {
    "bot_id": "string",
    "api_key": "string",
    "api_secret": "string",
    "exchange": "string",
    "testnet": boolean
  }

GET /bot-api/status/{bot_id}
- Get status of a connected bot

DELETE /bot-api/disconnect/{bot_id}
- Disconnect a trading bot
```

### Statistics
```
GET /stats
- Returns aggregated system statistics
```

## 🎨 UI Features

### Modern Design
- **Dark Theme**: Sleek dark interface with neon accents
- **Glass Morphism**: Modern frosted glass effect on panels
- **Smooth Animations**: Elegant transitions and pulses
- **Responsive Layout**: Works on desktop, tablet, and mobile

### Color Scheme
- **Neon Blue**: `#00d9ff` - Primary accent
- **Neon Purple**: `#d946ef` - Secondary accent
- **Neon Green**: `#22c55e` - Success/healthy status
- **Neon Red**: `#ef4444` - Danger/alerts

## 🔐 Security Considerations

### API Security
- All API endpoints accept requests from any origin (CORS enabled)
- Consider restricting CORS in production with specific domains
- Bot API credentials are stored in Redis with a 24-hour expiration for local/demo use
- For production, add encryption at rest and restrict credential permissions before using live exchange keys

### Trading Bot API
- API credentials are stored temporarily in Redis
- Only read-only permissions required
- Testnet recommended for initial setup
- Auto-expiration of credentials after 24 hours

## 📊 Data Flow

```
Trading Bot (Python)
    ↓
Redis Streams (Telemetry & Events)
    ↓
FastAPI Backend (Data retrieval & processing)
    ↓
React Frontend (Real-time visualization)
    ↓
User Dashboard
```

## 🛠️ Configuration

### Environment Variables

**Frontend** (via `.env` or `.env.local`):
```
VITE_API_URL=http://localhost:8000
```

If `VITE_API_URL` is not set, the React app uses `/api`. In Docker, Nginx proxies `/api/*` to the FastAPI service. During local Vite development, `/api/*` is proxied to `http://localhost:8000`.

**API** (via Docker environment or `.env`):
```
REDIS_HOST=redis
REDIS_PORT=6379
```

## 📱 Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

## 🐛 Troubleshooting

### Frontend won't connect to API
1. Check API is running: `curl http://localhost:8000/health`
2. Verify Redis connection: `redis-cli ping`
3. Check CORS headers in browser console

### Empty telemetry data
1. Ensure trading bot is running
2. Check Redis has data: `redis-cli xlen bot_telemetry`
3. Verify sentinel is running: `docker logs algo_sentinel`

### Docker build fails
```bash
# Clean up Docker
docker system prune -a

# Rebuild
docker compose build --no-cache
docker compose up -d
```

## 📈 Performance Tips

1. **Limit telemetry data**: Use `limit` parameter to reduce payload
2. **Caching**: Frontend caches recent data for 3 seconds
3. **Polling**: Adjust refresh intervals in components as needed
4. **Database**: Redis Streams are optimized for real-time data

## 🔄 Comparison: Streamlit vs React

| Feature | Streamlit | React |
|---------|-----------|-------|
| Performance | Good | Excellent |
| Customization | Limited | Unlimited |
| Real-time Updates | Good | Excellent |
| Learning Curve | Steep | Moderate |
| Bundle Size | Larger | Smaller |
| Mobile Experience | Fair | Excellent |
| UI/UX | Basic | Modern |

## 📚 Additional Resources

- [React Documentation](https://react.dev)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Tailwind CSS](https://tailwindcss.com)
- [Redis Streams](https://redis.io/docs/data-types/streams)
- [Recharts](https://recharts.org)

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs: `docker logs <container_name>`
3. Verify Redis connection: `redis-cli`
4. Check API health: `curl http://localhost:8000/health`

---

**Version**: 1.0.0  
**Last Updated**: June 2024  
**Status**: Production Ready ✅
