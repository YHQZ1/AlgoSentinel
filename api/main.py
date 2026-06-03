from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import redis
import os
from datetime import datetime

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
STREAM_NAME = "bot_telemetry"
EVENT_STREAM = "system_events"
COMMAND_CHANNEL = "bot_commands"

# Initialize FastAPI
app = FastAPI(title="AlgoSentinel API", description="AI-Powered Risk Management for Trading Bots")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Models
class TelemetryData(BaseModel):
    trade_freq: float
    volatility: float
    order_cancel_rate: float
    latency: float
    mode: str
    session_id: str

class EventData(BaseModel):
    timestamp: Optional[str]
    event_type: str
    message: str
    action: Optional[str]
    raw_error: Optional[str]
    smoothed_error: Optional[str]
    threshold: Optional[str]
    action_delay: Optional[str]
    session_id: str

class CommandRequest(BaseModel):
    command: str  # FORCE_ROGUE, KILL_SURE, RESET_BOT

class TradingBotAPIConfig(BaseModel):
    api_key: str
    api_secret: str
    exchange: str  # e.g., "binance", "coinbase"
    testnet: bool = False
    bot_id: str

class HealthResponse(BaseModel):
    status: str
    redis_connected: bool
    timestamp: str

# Utility functions
def parse_timestamp(value):
    try:
        return datetime.fromtimestamp(float(value))
    except Exception:
        return None

def load_telemetry(count=300) -> List[TelemetryData]:
    try:
        logs = r.xrevrange(STREAM_NAME, count=count)
    except Exception:
        return []
    result = []
    for _, content in logs:
        result.append(TelemetryData(
            trade_freq=float(content.get("trade_freq", 0)),
            volatility=float(content.get("volatility", 0)),
            order_cancel_rate=float(content.get("order_cancel_rate", 0)),
            latency=float(content.get("latency", 0)),
            mode=content.get("mode", "HEALTHY"),
            session_id=content.get("session_id", "unknown")
        ))
    return result[::-1]

def load_events(count=50) -> List[EventData]:
    try:
        events = r.xrevrange(EVENT_STREAM, count=count)
    except Exception:
        return []
    result = []
    for _, content in events:
        ts = parse_timestamp(content.get("timestamp", "0"))
        result.append(EventData(
            timestamp=ts.isoformat() if ts else None,
            event_type=content.get("event_type", "unknown"),
            message=content.get("message", ""),
            action=content.get("action"),
            raw_error=content.get("raw_error"),
            smoothed_error=content.get("smoothed_error"),
            threshold=content.get("threshold"),
            action_delay=content.get("action_delay"),
            session_id=content.get("session_id", "unknown")
        ))
    return result[::-1]

def humanize_status(event: EventData) -> str:
    event_type = event.event_type
    action = event.action or ""
    if event_type == "ANOMALY_ACTION":
        if action == "KILL_SURE":
            return "🛑 Kill switch executed. Trading halted to avoid catastrophic risk."
        if action == "FLATTEN_POSITIONS":
            return "📉 Positions flattened to reduce exposure."
        if action == "SLOW_DOWN":
            return "⚠️ Speed reduced to limit risk while observing behavior."
    if event_type == "CALIBRATION_COMPLETE":
        return "✅ Sentinel threshold calibrated successfully."
    if event_type in {"SESSION_START", "SESSION_CHANGE"}:
        return f"🔄 {event.message}"
    return event.message or "No event data."

def average(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0

# API Endpoints

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API and Redis connection status"""
    try:
        r.ping()
        redis_connected = True
    except Exception:
        redis_connected = False
    
    return HealthResponse(
        status="online" if redis_connected else "degraded",
        redis_connected=redis_connected,
        timestamp=datetime.now().isoformat()
    )

@app.get("/telemetry", response_model=List[TelemetryData])
async def get_telemetry(limit: int = 300):
    """Get recent telemetry data from Redis"""
    try:
        return load_telemetry(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events", response_model=List[Dict[str, Any]])
async def get_events(limit: int = 50):
    """Get recent system events from Redis"""
    try:
        events = load_events(limit)
        return [
            {
                **event.dict(),
                "humanized": humanize_status(event)
            }
            for event in events
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/command")
async def send_command(request: CommandRequest):
    """Send a command to the bot"""
    try:
        valid_commands = ["FORCE_ROGUE", "KILL_SURE", "RESET_BOT"]
        if request.command not in valid_commands:
            raise HTTPException(status_code=400, detail=f"Invalid command. Must be one of {valid_commands}")
        
        r.publish(COMMAND_CHANNEL, request.command)
        
        command_descriptions = {
            "FORCE_ROGUE": "🚨 Rogue mode triggered. Sentinel should activate within seconds.",
            "KILL_SURE": "🛑 Manual kill-switch activated. All trading halted.",
            "RESET_BOT": "♻️ Bot reset initiated. System returning to healthy mode."
        }
        
        return {
            "status": "success",
            "command": request.command,
            "message": command_descriptions.get(request.command),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bot-api/config")
async def configure_bot_api(config: TradingBotAPIConfig, background_tasks: BackgroundTasks):
    """Configure and connect to a real trading bot API"""
    try:
        # Store bot API configuration in Redis
        bot_config_key = f"bot_api_config:{config.bot_id}"
        r.hset(bot_config_key, mapping={
            "api_key": config.api_key,
            "api_secret": config.api_secret,
            "exchange": config.exchange,
            "testnet": str(config.testnet),
            "connected_at": str(datetime.now().isoformat()),
            "status": "CONNECTED"
        })
        
        # Set expiration for security (24 hours)
        r.expire(bot_config_key, 86400)
        
        # Log the connection event
        r.xadd("bot_api_events", {
            "event_type": "BOT_API_CONNECTED",
            "bot_id": config.bot_id,
            "exchange": config.exchange,
            "testnet": str(config.testnet),
            "timestamp": str(datetime.now().isoformat())
        })
        
        # Publish notification to system
        r.publish(COMMAND_CHANNEL, f"BOT_API_CONNECTED:{config.bot_id}")
        
        return {
            "status": "success",
            "message": f"Connected to {config.exchange} API for bot {config.bot_id}",
            "bot_id": config.bot_id,
            "exchange": config.exchange,
            "testnet": config.testnet,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bot-api/status/{bot_id}")
async def get_bot_api_status(bot_id: str):
    """Get the status of a connected trading bot API"""
    try:
        bot_config_key = f"bot_api_config:{bot_id}"
        config = r.hgetall(bot_config_key)
        
        if not config:
            return {
                "status": "disconnected",
                "bot_id": bot_id,
                "connected": False
            }
        
        return {
            "status": config.get("status", "unknown"),
            "bot_id": bot_id,
            "exchange": config.get("exchange"),
            "testnet": config.get("testnet") == "True",
            "connected_at": config.get("connected_at"),
            "connected": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/bot-api/disconnect/{bot_id}")
async def disconnect_bot_api(bot_id: str):
    """Disconnect a trading bot API"""
    try:
        bot_config_key = f"bot_api_config:{bot_id}"
        r.delete(bot_config_key)
        
        # Log the disconnection event
        r.xadd("bot_api_events", {
            "event_type": "BOT_API_DISCONNECTED",
            "bot_id": bot_id,
            "timestamp": str(datetime.now().isoformat())
        })
        
        return {
            "status": "success",
            "message": f"Disconnected from trading bot API: {bot_id}",
            "bot_id": bot_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        telemetry = load_telemetry(count=300)
        events = load_events(count=50)
        
        if not telemetry:
            return {
                "total_records": 0,
                "total_events": len(events),
                "avg_trade_freq": 0,
                "avg_volatility": 0,
                "avg_latency": 0
            }
        
        trade_freqs = [t.trade_freq for t in telemetry]
        volatilities = [t.volatility for t in telemetry]
        latencies = [t.latency for t in telemetry]
        
        return {
            "total_records": len(telemetry),
            "total_events": len(events),
            "avg_trade_freq": average(trade_freqs),
            "avg_volatility": average(volatilities),
            "avg_latency": average(latencies),
            "max_trade_freq": max(trade_freqs),
            "max_volatility": max(volatilities),
            "max_latency": max(latencies),
            "anomaly_events": sum(1 for e in events if e.event_type == "ANOMALY_ACTION"),
            "kill_switch_events": sum(1 for e in events if e.action == "KILL_SURE")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
