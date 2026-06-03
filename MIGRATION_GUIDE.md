# AlgoSentinel React Frontend - Migration & Integration Guide

## 🎯 What's New

The React frontend replaces the Streamlit dashboard with a modern, high-performance web application featuring:

✅ **All existing Streamlit functionality** - 100% parity with original dashboard
✅ **Modern UI/UX** - Sleek dark theme with neon accents and glass morphism
✅ **Real-time Updates** - Live charts and data refresh every 3 seconds
✅ **Trading Bot API Integration** - Connect and monitor real trading bots
✅ **Responsive Design** - Works perfectly on desktop, tablet, and mobile
✅ **Better Performance** - Optimized React components with minimal re-renders
✅ **TypeScript** - Full type safety for better development experience
✅ **Tailwind CSS** - Utility-first styling for rapid UI development

## 📦 New Project Structure

```
AlgoSentinel/
├── api/                    # NEW: FastAPI Backend
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # NEW: React Frontend
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── index.css
│   │   ├── api/
│   │   │   └── client.ts
│   │   └── components/
│   │       ├── Dashboard.tsx
│   │       ├── EventLog.tsx
│   │       ├── Statistics.tsx
│   │       ├── Controls.tsx
│   │       └── BotAPIConfig.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.cjs
│   ├── Dockerfile
│   └── index.html
├── bot/                    # Existing: Trading Bot
├── sentinel/               # Existing: AI Sentinel
├── dashboard/              # Legacy: Streamlit (kept for compatibility)
├── docker-compose.yml      # Updated: Now includes API & Frontend
├── REACT_SETUP.md          # NEW: React setup guide
├── MIGRATION_GUIDE.md      # NEW: This file
├── dev-start.sh            # NEW: Local dev startup script
└── docker-start.sh         # NEW: Docker startup script
```

## 🔄 Migration Path

### Option 1: Run Both (Recommended for transition)
```bash
docker compose up -d
# Access both:
# New React UI: http://localhost:3000
# Old Streamlit: http://localhost:8501
```

### Option 2: Replace Completely
1. Remove or comment out dashboard service in `docker-compose.yml`
2. Only React frontend will be available at `http://localhost:3000`

### Option 3: Local Development
```bash
./dev-start.sh
```

## 🔗 API Integration

The React frontend communicates with a new FastAPI backend that wraps Redis:

### Architecture
```
React Frontend
     ↓
FastAPI Backend
     ↓
Redis Streams
     ↓
Trading Bot & Sentinel
```

### API Endpoints Available

All endpoints are RESTful and documented at `http://localhost:8000/docs`

```
GET  /health              - Check API status
GET  /telemetry          - Get telemetry data
GET  /events             - Get system events
POST /command            - Send bot commands
POST /bot-api/config     - Configure bot API
GET  /bot-api/status/{id} - Check bot status
DELETE /bot-api/disconnect/{id} - Disconnect bot
GET  /stats              - Get statistics
```

## 🆕 Trading Bot API Feature

### What It Does
When you provide a trading bot API configuration, AlgoSentinel will:
1. Store your credentials securely (24-hour expiration)
2. Begin monitoring your bot's telemetry in real-time
3. Automatically trigger risk management actions if anomalies detected
4. Show live data in the Dashboard

### Supported Exchanges
- Binance
- Coinbase
- Kraken
- Bitfinex
- Huobi

### Setup Steps
1. Go to "Bot API" tab
2. Enter your bot ID (e.g., "my-trading-bot-1")
3. Provide API key and secret (read-only recommended)
4. Select exchange and enable testnet for testing
5. Click "Connect Bot"
6. Bot data will appear in Dashboard

### Security Notes
- Only read-only API permissions needed
- Credentials stored in Redis with auto-expiration
- No credentials logged or transmitted to external services
- Use HTTPS/TLS in production for encrypted transport

## 📊 Feature Comparison

| Feature | Streamlit | React |
|---------|-----------|-------|
| Dashboard | ✅ | ✅ |
| Events Log | ✅ | ✅ Enhanced |
| Statistics | ✅ | ✅ Enhanced |
| Controls | ✅ | ✅ |
| Bot API Config | ❌ | ✅ NEW |
| Real-time Charts | ✅ | ✅ Optimized |
| Mobile Support | Limited | ✅ Full |
| Performance | Good | Excellent |
| Customization | Limited | Unlimited |
| Type Safety | ❌ | ✅ TypeScript |

## 🚀 Deployment

### Docker Production Build
```bash
docker compose build
docker compose up -d

# Verify services
curl http://localhost:3000
curl http://localhost:8000/health
```

### Manual Production Deployment

**Frontend:**
```bash
cd frontend
npm install
npm run build
npm install -g serve
serve -s dist -l 3000
```

**API:**
```bash
cd api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔐 Environment Configuration

### Frontend (.env or .env.local)
```
VITE_API_URL=http://your-api-domain.com:8000
```

### API (Docker env or .env)
```
REDIS_HOST=redis
REDIS_PORT=6379
```

## ⚙️ Advanced Configuration

### API CORS
To restrict CORS in production, edit `api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend API URL
For production, update API URL in:
- `frontend/vite.config.ts` for development
- `.env.production` for build-time configuration
- Environment variable `VITE_API_URL`

### SSL/HTTPS
Behind a reverse proxy (nginx/Apache):
1. Configure proxy to forward requests
2. Update VITE_API_URL to use https
3. Ensure CORS headers properly set

## 📈 Performance Optimizations

### Frontend
- Lazy loading of components
- Memoized components to prevent re-renders
- Efficient data fetching with 3-second intervals
- Optimized charts with Recharts
- CSS-in-JS with Tailwind for minimal bundle

### API
- Connection pooling for Redis
- Efficient stream queries
- Response caching where appropriate
- Request throttling for telemetry endpoints

### Redis
- Efficient XREADGROUP for stream consumption
- TTL-based key expiration for API configs
- Stream compression via XTRIM

## 🐛 Troubleshooting Migration

### Frontend shows "Connection Error"
```bash
# Check API is running
curl http://localhost:8000/health

# Check Redis
redis-cli ping

# View API logs
docker logs algo_api
```

### API returns 500 errors
```bash
# Check Redis connection
redis-cli -h redis ping

# View detailed logs
docker logs algo_api --tail 100

# Verify Redis has data
redis-cli -h redis xlen bot_telemetry
```

### Slow performance
```bash
# Check Redis performance
redis-cli info stats

# Monitor API requests
# Add debug logging in api/main.py

# Reduce telemetry limit in frontend
# Increase polling intervals if needed
```

## 🔄 Rollback Plan

If you need to roll back to Streamlit:

```bash
# Stop all services
docker compose down

# Edit docker-compose.yml to comment out:
# - api
# - frontend

# Only keep dashboard
docker compose up -d dashboard

# Streamlit will be available at http://localhost:8501
```

## 📚 Development Resources

### React
- Component-based architecture
- TypeScript for type safety
- Tailwind CSS for styling
- Custom hooks for logic reuse

### FastAPI
- Async/await for performance
- Pydantic for data validation
- OpenAPI/Swagger documentation
- CORS support

### Monitoring
- Use browser DevTools for frontend debugging
- Use `docker logs` for backend debugging
- Use `redis-cli` for Redis inspection

## ✅ Migration Checklist

- [ ] Review REACT_SETUP.md
- [ ] Build Docker images: `docker compose build`
- [ ] Start services: `docker compose up -d`
- [ ] Verify Frontend: http://localhost:3000
- [ ] Verify API: http://localhost:8000/health
- [ ] Test all Dashboard features
- [ ] Test all Controls commands
- [ ] Configure a bot in Bot API tab
- [ ] Monitor bot data in Dashboard
- [ ] Check Events and Statistics tabs
- [ ] Review logs for any errors
- [ ] Plan Streamlit migration/removal

## 🎓 Next Steps

1. **Customize Colors**: Edit `frontend/tailwind.config.cjs`
2. **Add New Features**: Create components in `frontend/src/components/`
3. **Extend API**: Add endpoints in `api/main.py`
4. **Deploy to Cloud**: Use Docker and container orchestration

## 📞 Support

For issues:
1. Check logs: `docker logs <service_name>`
2. Review REACT_SETUP.md and this guide
3. Test API directly: `curl http://localhost:8000/docs`
4. Verify Redis: `redis-cli` commands

---

**Migration Date**: June 2024
**Status**: Ready for Production ✅
**Backward Compatibility**: Streamlit dashboard still available
