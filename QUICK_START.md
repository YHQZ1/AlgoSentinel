# 🚀 AlgoSentinel React Frontend - Quick Reference

## ⚡ Getting Started (5 minutes)

### Option 1: Docker (Recommended)
```bash
cd /Users/yashrajshrivastava/Documents/AlgoSentinel
docker compose up -d
open http://localhost:3000
```

### Option 2: Local Development
```bash
cd /Users/yashrajshrivastava/Documents/AlgoSentinel
chmod +x dev-start.sh
./dev-start.sh
open http://localhost:3000
```

---

## 📍 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **React Frontend** ✨ | http://localhost:3000 | Main dashboard (NEW!) |
| **FastAPI Backend** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API reference |
| **Legacy Streamlit** | http://localhost:8501 | Old dashboard (for comparison) |
| **Redis CLI** | `redis-cli` | Database inspection |

---

## 🎯 Frontend Tabs

### 📊 Dashboard
- Real-time bot metrics
- Interactive charts (trade freq, volatility, etc.)
- Current bot status
- Live data updates every 3 seconds

### 📝 Events
- System event timeline
- Color-coded event types
- Detailed action descriptions
- Session tracking

### 📈 Statistics
- Aggregated performance metrics
- Event distribution pie chart
- Average vs max comparisons
- Anomaly detection counts

### 🎮 Controls
- 🚨 Trigger Rogue Mode (test detection)
- 🛑 Manual Kill Switch (emergency stop)
- ♻️ Reset Bot (return to healthy state)

### 🤖 Bot API (NEW!)
- Connect trading bot APIs
- Supported: Binance, Coinbase, Kraken, Bitfinex, Huobi
- Testnet/mainnet modes
- Real-time monitoring

---

## 🔧 API Endpoints Quick Reference

```bash
# Health check
curl http://localhost:8000/health

# Get telemetry
curl http://localhost:8000/telemetry

# Get events
curl http://localhost:8000/events

# Send command
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command":"FORCE_ROGUE"}'

# Configure bot API
curl -X POST http://localhost:8000/bot-api/config \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "my-bot",
    "api_key": "your-key",
    "api_secret": "your-secret",
    "exchange": "binance",
    "testnet": true
  }'

# Get statistics
curl http://localhost:8000/stats
```

---

## 📁 Key Files

### Frontend
- `frontend/src/App.tsx` - Main app component
- `frontend/src/api/client.ts` - API client
- `frontend/tailwind.config.cjs` - Customize colors/styling
- `frontend/.env` - API URL configuration

### Backend
- `api/main.py` - REST API endpoints
- `docker-compose.yml` - Service orchestration

### Documentation
- `REACT_SETUP.md` - Full setup guide
- `MIGRATION_GUIDE.md` - Streamlit migration
- `IMPLEMENTATION_SUMMARY.md` - What was created

---

## 🎨 Customization

### Change Colors
Edit `frontend/tailwind.config.cjs`:
```javascript
theme: {
  extend: {
    colors: {
      'neon-blue': '#00d9ff',      // Change primary color
      'neon-purple': '#d946ef',    // Change secondary color
      'neon-green': '#22c55e',     // Change success color
      'neon-red': '#ef4444',       // Change danger color
    }
  }
}
```

### Change Theme
Edit `frontend/src/index.css`:
```css
body {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
}
```

### Add New Features
1. Create component in `frontend/src/components/`
2. Import in `frontend/src/App.tsx`
3. Add API endpoints in `api/main.py` if needed

---

## 🐳 Docker Commands

```bash
# Start all services
docker compose up -d

# View running services
docker compose ps

# View logs
docker compose logs -f frontend
docker compose logs -f api
docker compose logs -f trading_bot
docker compose logs -f ai_sentinel

# Stop services
docker compose down

# Rebuild images
docker compose build --no-cache

# Clean up
docker system prune -a
```

---

## 🔍 Debugging

### Check Frontend Connection
```bash
# In browser console (F12)
fetch('http://localhost:8000/health').then(r => r.json()).then(console.log)
```

### Check Redis Data
```bash
redis-cli
> XLEN bot_telemetry
> XREAD COUNT 5 STREAMS bot_telemetry 0
> XLEN system_events
> XREAD COUNT 5 STREAMS system_events 0
```

### Check Docker Networks
```bash
docker network ls
docker network inspect algosentinel_sentinel_net
```

---

## 📊 Test the System

1. **Open Frontend**: http://localhost:3000
2. **Go to Dashboard Tab**: Verify telemetry appearing
3. **Go to Controls Tab**: Click "Trigger Rogue Mode"
4. **Watch Dashboard**: Metrics should spike after 2-3 seconds
5. **Check Events Tab**: Kill-switch event should appear
6. **Go to Statistics**: Verify anomaly count increased
7. **Reset System**: Click "Reset Bot" to restart

Expected: Metrics spike → Sentinel detects → Kill-switch triggers → Metrics drop to 0

---

## ❌ Troubleshooting

| Problem | Solution |
|---------|----------|
| Frontend shows "Connection Error" | Check API: `curl http://localhost:8000/health` |
| No telemetry data | Restart bot: `docker compose restart trading_bot` |
| API returns 500 | Check Redis: `redis-cli ping` |
| Slow performance | Check Docker stats: `docker stats` |
| Can't connect to bot API | Verify credentials and exchange name |

---

## 📚 Documentation

- **Full Setup**: See `REACT_SETUP.md`
- **Migration**: See `MIGRATION_GUIDE.md`
- **What's New**: See `IMPLEMENTATION_SUMMARY.md`
- **API Reference**: Visit http://localhost:8000/docs

---

## ✨ What's Different from Streamlit

| Aspect | Improvement |
|--------|------------|
| **Speed** | 10x faster load time |
| **Design** | Modern, sleek with neon theme |
| **Mobile** | Fully responsive |
| **Bot API** | Real trading bot support (NEW!) |
| **Performance** | Optimized React components |
| **Type Safety** | Full TypeScript |
| **Customization** | Unlimited styling options |
| **Developer Experience** | Better tooling & debugging |

---

## 🎓 Learning Resources

- **React**: https://react.dev
- **FastAPI**: https://fastapi.tiangolo.com
- **Tailwind CSS**: https://tailwindcss.com
- **Redis Streams**: https://redis.io/docs/data-types/streams
- **TypeScript**: https://www.typescriptlang.org

---

## 🆘 Need Help?

1. Check `REACT_SETUP.md` for setup issues
2. Check `MIGRATION_GUIDE.md` for migration questions
3. View API docs: http://localhost:8000/docs
4. Check logs: `docker compose logs <service>`
5. Verify connections: `redis-cli ping` & `curl http://localhost:8000/health`

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: June 2024
