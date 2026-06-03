# 🛡️ AlgoSentinel: AI-Powered Risk Management System

**Real-time anomaly detection for trading bots with autonomous kill-switch capability.**

AlgoSentinel is a production-grade risk management system that monitors trading bot behavior in real-time, detects anomalies using a PyTorch-based TCN Autoencoder, and automatically triggers protective actions including position flattening and bot shutdown.

## ✨ NEW: Modern React Frontend + FastAPI Backend

AlgoSentinel now includes a **modern React-based dashboard** with a **FastAPI backend**, replacing the legacy Streamlit interface!

### 🎨 What's New

- **React Frontend**: Modern, sleek UI with neon accents and glass morphism effects
- **FastAPI Backend**: High-performance REST API with async support
- **Trading Bot API Integration**: Connect real trading bots for live monitoring
- **Real-time Charts**: Interactive visualizations with Recharts
- **Full TypeScript**: Type-safe codebase with better developer experience
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Tailwind CSS**: Beautiful, utility-first styling

### 📍 Access Points (Docker)

```
🎨 React Frontend:     http://localhost:3000
🔗 FastAPI Backend:    http://localhost:8000
📚 API Documentation:  http://localhost:8000/docs
📊 Legacy Streamlit:   http://localhost:8501 (kept for compatibility)
```

### 📚 Documentation

- **[React Setup Guide](./REACT_SETUP.md)** - Complete React/API setup instructions
- **[Migration Guide](./MIGRATION_GUIDE.md)** - Migration from Streamlit to React

---

## 🎯 Features

- **AI-Powered Anomaly Detection**: TCN Autoencoder trained on healthy bot telemetry
- **Real-Time Monitoring**: Sub-second latency anomaly detection via Redis Streams
- **Autonomous Kill-Switch**: Graduated response system (SLOW_DOWN → FLATTEN_POSITIONS → KILL_SURE)
- **Dynamic Threshold Calibration**: 95th percentile-based adaptive thresholds
- **Modern Dashboard**: Real-time metrics, event sequencing, and bot control (React + FastAPI)
- **Trading Bot API Support**: Connect and monitor real trading bots in production
- **Stream-Based Architecture**: Scalable consumer group pattern with fresh data consumption
- **Event Logging**: Complete audit trail of all sentinel actions and bot state changes

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       AlgoSentinel System                        │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ Trading Bot  │
    │  (Python)    │
    └──────┬───────┘
           │ Telemetry XADD
           ▼
    ┌──────────────────────┐
    │   Redis Streams      │
    │  bot_telemetry       │
    │  system_events       │
    │  (Persistence)       │
    └──────┬──────────────┬─┘
           │              │
      XREADGROUP      XREADGROUP
           │              │
    ┌──────▼──────┐  ┌────▼──────────────┐
    │  Sentinel   │  │  FastAPI Backend  │
    │  (Detector) │  │  (New: REST API)  │
    └──────┬──────┘  └────┬──────────────┘
           │              │
           │ PubSub       │ HTTP/JSON
           │ COMMAND_     │ Real-time Data
           │ CHANNEL      │
           ▼              ▼
    ┌──────────────────────────┐
    │   React Frontend (UI)    │
    │  ├─ Dashboard            │
    │  ├─ Events Log           │
    │  ├─ Statistics           │
    │  ├─ Controls             │
    │  └─ Bot API Config       │
    └──────────────────────────┘
           │
    ┌──────▼──────────────────┐
    │   Trading Bot / Sentinel│
    │  Receives: KILL_SURE    │
    │  Receives: SLOW_DOWN    │
    │  Receives: FLATTEN_POS  │
    └─────────────────────────┘
```

---

## 🏗️ Components

### 1. **Trading Bot** (`bot/main.py`)
- Generates 4-channel telemetry: trade frequency, volatility, cancel rate, latency
- Reports via Redis XADD to `bot_telemetry` stream with session tracking
- Listens on Redis Pub/Sub for sentinel commands
- Simulates 3 modes:
  - **HEALTHY**: Normal trading (0.1-0.5 freq, 0.01-0.02 volatility)
  - **ROGUE**: Anomalous behavior (60-120 freq, 0.30-0.75 volatility)
  - **KILLED**: Zeroed telemetry after receiving KILL_SURE

### 2. **AI Sentinel** (`sentinel/main.py`)
- TCN Autoencoder: 4-input → 48-sequence encoder/decoder on PyTorch
- **Calibration Phase** (60 samples): Learns healthy reconstruction baseline
- **Detection Phase** (continuous): 
  - Computes reconstruction error for each data point
  - Applies exponential smoothing (α=0.30) to noise reduction
  - Requires 2 consecutive alerts before action (gating)
  - Publishes to system_events stream for audit trail

### 3. **FastAPI Backend** (`api/main.py`)
- Serves health, telemetry, events, command, statistics, and bot API endpoints
- Reads Redis Streams and returns JSON to the React frontend
- Publishes control commands to the trading bot through Redis Pub/Sub
- Stores demo bot API configuration temporarily in Redis with a 24-hour expiration

### 4. **React Dashboard** (`frontend/`)
- Modern dashboard with real-time telemetry charts and statistics
- Event log with humanized sentinel actions
- Control panel for rogue mode, kill switch, and bot reset
- Bot API configuration screen for exchange/testnet setup
- Production Docker image serves static assets with Nginx and proxies `/api/*` to FastAPI

### 5. **Legacy Streamlit Dashboard** (`dashboard/app.py`)
- Kept for compatibility and comparison while the React dashboard is the primary UI
- Real-time metrics display, event sequence visualization, and system controls

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Redis (included in Docker)
- Node.js 18+ (for local frontend development)

### Installation & Deployment

#### Option 1: Docker (Recommended - All Services)

```bash
# Clone the repository
git clone https://github.com/YashrajSh/AlgoSentinel.git
cd AlgoSentinel

# Start all services
docker compose up -d

# Wait for containers to start (~30 seconds)

# Access the system:
# React Frontend:    http://localhost:3000 ✨ (NEW!)
# FastAPI Backend:   http://localhost:8000
# API Docs:          http://localhost:8000/docs
# Legacy Streamlit:  http://localhost:8501 (for comparison)

# View dashboard
open http://localhost:3000
```

#### Option 2: Local Development (Frontend + Docker Backend)

```bash
# Start backend services only
docker compose up -d redis trading_bot ai_sentinel api

# In another terminal, start frontend dev server
cd frontend
npm install
npm run dev

# Frontend available at http://localhost:3000
# API available at http://localhost:8000
```

#### Option 3: Use Startup Scripts

```bash
# Make scripts executable
chmod +x dev-start.sh docker-start.sh

# Option A: Local development
./dev-start.sh

# Option B: Docker deployment
./docker-start.sh
```

### Verify Deployment
```bash
# Check all containers running
docker compose ps

# Check frontend health
curl http://localhost:3000

# Check API health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# View bot telemetry in Redis
docker compose exec redis redis-cli
> XLEN bot_telemetry
> XLEN system_events

# Check sentinel logs
docker compose logs -f ai_sentinel

# Check bot logs
docker compose logs -f trading_bot

# Check API logs
docker compose logs -f api
```

---

## 📊 Live Demo

### React Frontend Features

1. **Dashboard Tab** (`http://localhost:3000`)
   - Real-time telemetry metrics (trade frequency, volatility, cancel rate, latency)
   - Interactive charts showing market metrics and risk indicators
   - Current bot status and session information

2. **Events Tab**
   - Complete event log with color-coded entries
   - Humanized event descriptions
   - Timeline view of all system actions

3. **Statistics Tab**
   - Aggregated performance metrics
   - Event distribution pie chart
   - Average vs maximum comparisons

4. **Controls Tab** (Same as Streamlit)
   - 🚨 **Trigger Rogue Mode**: Force anomalous behavior for testing
   - 🛑 **Manual Kill Switch**: Emergency stop with immediate action
   - ♻️ **Reset Bot**: Return to healthy baseline

5. **Bot API Tab** (NEW!)
   - Connect trading bots from real exchanges
   - Supported: Binance, Coinbase, Kraken, Bitfinex, Huobi
   - Testnet and mainnet support
   - Real-time monitoring and risk management

### Trigger Complete Kill-Flow (React Frontend):

1. **Open Dashboard**: http://localhost:3000

2. **Go to Controls Tab → Click "🚨 Trigger Rogue Mode"**
   - Dashboard shows: Current Mode → ROGUE
   - Charts update to show anomalous behavior

3. **Sentinel Detects Anomaly** (2-3 seconds)
   - Reconstruction error exceeds threshold
   - Events Tab shows detection event

4. **Bot Receives Kill Command**
   - Events Tab: Detailed kill-switch event
   - Dashboard: All metrics drop to zero
   - Mode changes to KILLED

5. **Reset System**
   - Controls Tab → Click "♻️ Reset Bot"
   - System returns to HEALTHY mode
   - New session ID issued

### Connect a Real Trading Bot:

1. **Go to Bot API Tab**
2. **Enter Bot Details:**
   - Bot ID: `my-trading-bot-1`
   - Exchange: `binance` (or your exchange)
   - API Key: (from exchange)
   - API Secret: (from exchange)
   - Testnet: ✅ (enable for testing)
3. **Click "Connect Bot"**
4. **Monitor in Dashboard**
   - Real-time bot telemetry appears
   - Sentinel automatically monitors for anomalies
   - Protective actions trigger if needed

**Expected Timeline**: ROGUE → Detection (2-3s) → KILL_SURE → Bot Killed → Graph drops

---

## ⚙️ Configuration

### Sentinel Parameters (`sentinel/main.py`)

```python
# Calibration & Threshold
CALIBRATION_SAMPLES = 60          # Warmup samples for baseline
PERCENTILE_THRESHOLD = 95         # 95th percentile for normal behavior
MIN_THRESHOLD = 0.05              # Floor to prevent false negatives

# Smoothing & Gating
ERROR_SMOOTHING_ALPHA = 0.30      # Exponential smoothing factor
CONSECUTIVE_ALERTS_TO_TRIGGER = 2 # Alerts needed before action
ALERT_COOLDOWN_SECONDS = 5.0      # Prevent trigger spam

# Action Thresholds (vs smoothed error)
KILL_THRESHOLD_MULTIPLIER = 3.0   # 3x → KILL_SURE
FLATTEN_THRESHOLD_MULTIPLIER = 1.5  # 1.5x → FLATTEN_POSITIONS
```

### Bot Parameters (`bot/main.py`)

```python
# Telemetry Generation
HEALTHY_MODE = {
    'trade_freq': (0.1, 0.5),           # Requests/sec
    'volatility': (0.01, 0.02),         # Market vol
    'order_cancel_rate': (0.05, 0.15),  # % cancelled
    'latency': (0.001, 0.005)           # Seconds
}

ROGUE_MODE = {
    'trade_freq': (60, 120),            # 100x+ spike
    'volatility': (0.30, 0.75),         # High vol
    'order_cancel_rate': (0.75, 0.99),  # Cancelling most orders
    'latency': (0.02, 0.10)             # Slow responses
}

KILLED_MODE = {
    'all_metrics': 0.0                  # Zeroed out
}
```

## 📈 Monitoring & Debugging

### View Redis Streams

```bash
# Connect to Redis
docker compose exec redis redis-cli

# Check telemetry stream
XLEN bot_telemetry              # Entry count
XREAD COUNT 5 STREAMS bot_telemetry 0    # Last 5 entries

# Check system events
XLEN system_events
XREAD COUNT 10 STREAMS system_events 0   # Last 10 events

# Check consumer groups
XINFO GROUPS bot_telemetry
```

### Check Service Logs

```bash
# Follow sentinel detection logs
docker compose logs -f ai_sentinel

# Follow bot command reception
docker compose logs -f trading_bot

# Follow dashboard updates
docker compose logs -f dashboard
```

### Dashboard Metrics Explained

| Metric | Range | Alert Level |
|--------|-------|------------|
| Trade Frequency | 0.1-0.5 (healthy) | ⚠️ HIGH >50 |
| Volatility | 0.01-0.02 (stable) | 🔥 CRITICAL >0.30 |
| Cancel Rate | 5-15% (normal) | 🚨 DANGER >70% |
| Latency | 1-5ms (fast) | ⏰ LAGGING >10ms |

## 🔍 How Anomaly Detection Works

### 1. **TCN Autoencoder Architecture**

```
Input (4 channels × 48 timesteps)
    ↓
Encoder:
  Conv1d(1→16, kernel=3)
  ReLU + MaxPool
  Conv1d(16→8, kernel=3)
  ReLU + MaxPool
  Bottleneck (8D)
    ↓
Decoder:
  ConvTranspose1d(8→16)
  ReLU
  ConvTranspose1d(16→1)
    ↓
Reconstruction Loss = MSE(input, output)
```

### 2. **Detection Pipeline**

```
Healthy Telemetry          Rogue Telemetry
    ↓                           ↓
Pass through TCN          Pass through TCN
    ↓                           ↓
Low Error (~0.05)         High Error (~0.8+)
    ↓                           ↓
Below Threshold            Exceeds 3x Threshold
    ↓                           ↓
✅ Allow Trading          🚨 TRIGGER KILL_SURE
```

### 3. **Smoothing & Gating**

```
Raw Error: [0.05, 0.04, 0.85, 0.92, 0.88, ...]
    ↓
Exponential Smoothing (α=0.30):
    s₁ = 0.05
    s₂ = 0.30×0.04 + 0.70×0.05 = 0.047
    s₃ = 0.30×0.85 + 0.70×0.047 = 0.288
    s₄ = 0.30×0.92 + 0.70×0.288 = 0.476
    ↓
Smoothed: [0.05, 0.047, 0.288, 0.476, ...]
    ↓
Alert Count: 0 → 0 → 1 → 2 (trigger threshold reached!)
    ↓
🔥 ACTION: KILL_SURE
```

## 📝 Event Stream Schema

### `bot_telemetry` Stream
```json
{
  "trade_freq": "0.25",
  "volatility": "0.0150",
  "order_cancel_rate": "0.108",
  "latency": "0.00234",
  "mode": "HEALTHY",
  "session_id": "b4c1841202524cda88a07c18bd94cbeb"
}
```

### `system_events` Stream
```json
{
  "timestamp": "1716360000.123",
  "event_type": "ANOMALY_ACTION|BOT_COMMAND|CALIBRATION_COMPLETE|SESSION_START",
  "action": "KILL_SURE|SLOW_DOWN|FLATTEN_POSITIONS|FORCE_ROGUE|RESET_BOT",
  "message": "Human readable description",
  "raw_error": "0.847",
  "smoothed_error": "0.476",
  "threshold": "0.7057",
  "action_delay": "2.34",
  "session_id": "b4c1841202524cda88a07c18bd94cbeb"
}
```

## 🛠️ Development

### Local Setup (without Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r sentinel/requirements.txt
pip install -r bot/requirements.txt
pip install -r dashboard/requirements.txt

# Start Redis separately
redis-server

# Run services individually
python bot/main.py
python sentinel/main.py
streamlit run dashboard/app.py
```

### Training the Model

The model is pre-trained and included as `sentinel_model.pth`. To retrain:

```bash
python train_model.py  # Uses healthy_bot_data.csv
```

### Dataset

- `healthy_bot_data.csv`: 5000+ samples of healthy bot telemetry
- `train_sequences_v2.npy`: Preprocessed sequences (shape: [5000, 48, 4])
- `global_min.npy`, `global_max.npy`: Normalization bounds

## 📊 Project Structure

```
AlgoSentinel/
├── api/                        # NEW: FastAPI Backend
│   ├── main.py                 # REST API endpoints
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile
├── frontend/                   # NEW: React Frontend
│   ├── src/
│   │   ├── App.tsx             # Main React component
│   │   ├── main.tsx            # React entry point
│   │   ├── index.css           # Global styles + Tailwind
│   │   ├── api/
│   │   │   └── client.ts       # API client (axios)
│   │   └── components/
│   │       ├── Dashboard.tsx   # Real-time telemetry
│   │       ├── EventLog.tsx    # System events
│   │       ├── Statistics.tsx  # Aggregated metrics
│   │       ├── Controls.tsx    # Bot commands
│   │       └── BotAPIConfig.tsx # Trading bot setup
│   ├── package.json            # Dependencies
│   ├── vite.config.ts          # Vite build config
│   ├── tailwind.config.cjs     # Tailwind CSS config
│   ├── tsconfig.json           # TypeScript config
│   ├── index.html
│   ├── Dockerfile
│   └── .env.example
├── bot/
│   ├── main.py                 # Trading bot simulation
│   ├── Dockerfile
│   └── requirements.txt
├── sentinel/
│   ├── main.py                 # Anomaly detection engine
│   ├── Dockerfile
│   └── requirements.txt
├── dashboard/                  # Legacy Streamlit (kept for compatibility)
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml          # Service orchestration (updated)
├── REACT_SETUP.md              # NEW: React setup guide
├── MIGRATION_GUIDE.md          # NEW: Migration from Streamlit
├── dev-start.sh                # NEW: Local dev startup script
├── docker-start.sh             # NEW: Docker startup script
├── train_model.py              # Model training script
├── preprocess.py               # Data preprocessing
├── collect_data.py             # Training data collection
├── eval_model.py               # Model evaluation
├── sentinel_model.pth          # Pre-trained TCN Autoencoder
├── healthy_bot_data.csv        # Training dataset
├── train_sequences_v2.npy      # Preprocessed sequences
├── global_min.npy              # Normalization min bounds
├── global_max.npy              # Normalization max bounds
└── README.md
```

## 🔐 Security Considerations

- **Redis Authentication**: Configure `requirepass` for production
- **Pub/Sub Validation**: Commands validated before execution
- **Consumer Groups**: Isolated telemetry streams prevent duplicate reads
- **Audit Trail**: All actions logged to `system_events` for compliance
- **Session Tracking**: Each bot session gets unique ID for attribution

## 🚦 Troubleshooting

### Dashboard Not Showing Data

```bash
# Check Redis connectivity
docker compose exec dashboard ping redis
# Should ping successfully

# Verify telemetry stream exists
docker compose exec redis redis-cli XLEN bot_telemetry
# Should return > 0

# Check dashboard logs for errors
docker compose logs dashboard | tail -20
```

### Sentinel Not Triggering

```bash
# Verify sentinel is running
docker compose ps ai_sentinel
# Should show "Up"

# Check calibration happened
docker compose logs ai_sentinel | grep "Calibration complete"
# Should show threshold value

# Trigger rogue mode via dashboard and check logs
docker compose logs -f ai_sentinel
```

### Bot Not Receiving Commands

```bash
# Check bot is listening
docker compose logs bot | grep "Listening for"

# Manually publish test command
docker compose exec redis redis-cli
> PUBLISH bot_commands SLOW_DOWN

# Check bot receives it
docker compose logs -f trading_bot
```

## 📚 References

- **PyTorch TCN**: [Temporal Convolutional Networks for Time Series](https://arxiv.org/abs/1803.01271)
- **Redis Streams**: [Redis Stream Documentation](https://redis.io/topics/streams-intro)
- **Streamlit**: [Streamlit Documentation](https://docs.streamlit.io/)
- **Anomaly Detection**: [AutoEncoder for Anomaly Detection](https://www.kdnuggets.com/2022/06/anomaly-detection-autoencoders.html)

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

**Yashraj Shrivastava**

- GitHub: [@YashrajSh](https://github.com/YashrajSh)
- Project: AI-Powered Trading Bot Risk Management

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For issues, questions, or suggestions:
- Open an GitHub issue
- Check existing documentation above
- Review Docker logs for debugging

---

**Built with ❤️ for algorithmic trading safety.**
