import streamlit as st
import redis
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# Configuration
REDIS_HOST = "redis"  # Docker service name
REDIS_PORT = 6379
STREAM_NAME = "bot_telemetry"
EVENT_STREAM = "system_events"
COMMAND_CHANNEL = "bot_commands"

st.set_page_config(page_title="AlgoSentinel Control Center", layout="wide")

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

st.title("🛡️ AlgoSentinel: AI Risk Management")
st.markdown("---")

# --- SIDEBAR: SYSTEM CONTROLS ---
st.sidebar.header("⚙️ System Controls")
if st.sidebar.button("🚨 TRIGGER ROGUE MODE"):
    r.publish(COMMAND_CHANNEL, "FORCE_ROGUE")
    st.sidebar.warning("🚀 Rogue mode signal sent. Sentinel should trigger KILL_SURE within seconds.")

if st.sidebar.button("🛑 MANUAL KILL-SWITCH"):
    r.publish(COMMAND_CHANNEL, "KILL_SURE")
    st.sidebar.error("Manual kill signal sent.")

if st.sidebar.button("♻️ RESET BOT"):
    r.publish(COMMAND_CHANNEL, "RESET_BOT")
    st.sidebar.success("Reset command sent. Bot will restart into healthy mode.")

# --- UTILS ---

def parse_timestamp(value):
    try:
        return datetime.fromtimestamp(float(value))
    except Exception:
        return None


def load_telemetry(count=300):
    try:
        logs = r.xrevrange(STREAM_NAME, count=count)
    except Exception:
        return []
    result = []
    for _, content in logs:
        result.append({
            "trade_freq": float(content.get("trade_freq", 0)),
            "volatility": float(content.get("volatility", 0)),
            "order_cancel_rate": float(content.get("order_cancel_rate", 0)),
            "latency": float(content.get("latency", 0)),
            "mode": content.get("mode", "HEALTHY"),
            "session_id": content.get("session_id", "unknown")
        })
    return result[::-1]


def load_events(count=50):
    try:
        events = r.xrevrange(EVENT_STREAM, count=count)
    except Exception:
        return []
    result = []
    for _, content in events:
        ts = parse_timestamp(content.get("timestamp", "0"))
        result.append({
            "timestamp": ts,
            "event_type": content.get("event_type", "unknown"),
            "message": content.get("message", ""),
            "action": content.get("action", ""),
            "raw_error": content.get("raw_error", ""),
            "smoothed_error": content.get("smoothed_error", ""),
            "threshold": content.get("threshold", ""),
            "action_delay": content.get("action_delay", ""),
            "session_id": content.get("session_id", "unknown")
        })
    return result[::-1]


def humanize_status(event):
    event_type = event.get("event_type")
    action = event.get("action", "")
    if event_type == "ANOMALY_ACTION":
        if action == "KILL_SURE":
            return "Kill switch executed. Trading halted to avoid catastrophic risk."
        if action == "FLATTEN_POSITIONS":
            return "Positions flattened to reduce exposure."
        if action == "SLOW_DOWN":
            return "Speed reduced to limit risk while observing behavior."
    if event_type == "CALIBRATION_COMPLETE":
        return "Sentinel threshold calibrated successfully."
    if event_type in {"SESSION_START", "SESSION_CHANGE"}:
        return event.get("message", "New bot session event.")
    return event.get("message", "No event data.")


def format_loss_message(event):
    action = event.get("action", "")
    if action == "KILL_SURE":
        return "Estimated loss avoided: high. Bot was killed before dangerous execution."
    if action == "FLATTEN_POSITIONS":
        return "Potential exposure reduced; simulated loss avoided."
    if action == "SLOW_DOWN":
        return "Trading cadence slowed; no executed loss recorded."
    return "No active mitigation event recorded yet."


# --- LIVE DATA LOAD ---
telemetry = load_telemetry(300)
events = load_events(50)

latest_telemetry = telemetry[-1] if telemetry else None
latest_event = events[-1] if events else {}

# --- UPDATE METRICS ---
col1, col2, col3 = st.columns(3)
if latest_telemetry:
    mode = latest_telemetry.get("mode", "HEALTHY")
    mode_delta = "KILLED" if mode == "KILLED" else ("Rogue" if mode == "ROGUE" else "Healthy")
    col1.metric("🔴 Current Mode", mode, delta=mode_delta)
    col2.metric("Session ID", latest_telemetry.get("session_id", "unknown")[:8], delta="Live")
    col3.metric("Telemetry Count", f"{len(telemetry)}", delta="Updating")
else:
    col1.metric("🔴 Current Mode", "offline")
    col2.metric("Session ID", "none")
    col3.metric("Telemetry Count", "0")

st.markdown("---")

# --- PERFORMANCE METRICS ---
if latest_telemetry:
    freq = latest_telemetry.get("trade_freq", 0.0)
    vol = latest_telemetry.get("volatility", 0.0)
    can = latest_telemetry.get("order_cancel_rate", 0.0)
    lat = latest_telemetry.get("latency", 0.0)

    row1, row2, row3 = st.columns(3)
    row1.metric("📊 Trade Frequency", f"{freq:.2f} req/s", delta="HIGH ⚠️" if freq > 50.0 else ("High" if freq > 1.0 else "Normal"))
    row2.metric("📈 Volatility", f"{vol:.4f}", delta="CRITICAL 🔥" if vol > 0.30 else ("Critical" if vol > 0.10 else "Stable"))
    row3.metric("❌ Cancel Rate", f"{can:.2%}", delta="DANGER 🚨" if can > 0.70 else ("High" if can > 0.20 else "OK"))

    row4, row5, row6 = st.columns(3)
    row4.metric("⏱️ Latency", f"{lat*1000:.2f} ms", delta="Lagging" if lat > 10 else "Fast")
    row5.metric("Last Event", latest_event.get("event_type", "None"))
    row6.metric("Last Action", latest_event.get("action", "None"))

    if latest_event.get("action_delay"):
        st.caption(f"⏲️ Action delay: {latest_event.get('action_delay')} seconds")
else:
    st.info("Waiting for live telemetry from the bot...")

st.markdown("---")

if latest_telemetry and latest_telemetry.get("mode") == "KILLED":
    st.error("🚫 Bot is currently in KILLED mode. Telemetry is now zeroed out until RESET BOT is pressed.")
elif latest_telemetry and latest_telemetry.get("mode") == "ROGUE":
    st.warning("🚨 ROGUE MODE DETECTED. Sentinel should be sending KILL_SURE...")

# --- TELEMETRY CHART ---
st.subheader("📈 Live Telemetry Trend (Trade Frequency)")
if telemetry:
    df = pd.DataFrame(telemetry)
    fig = go.Figure()
    
    # Highlight killed zone
    if any(t["mode"] == "KILLED" for t in telemetry):
        killed_start = next((i for i, t in enumerate(telemetry) if t["mode"] == "KILLED"), None)
        if killed_start is not None:
            fig.add_vrect(x0=killed_start, x1=len(telemetry)-1, fillcolor="red", opacity=0.1, layer="below", line_width=0)
    
    # Highlight rogue zone
    if any(t["mode"] == "ROGUE" for t in telemetry):
        rogue_indices = [i for i, t in enumerate(telemetry) if t["mode"] == "ROGUE"]
        if rogue_indices:
            fig.add_vrect(x0=min(rogue_indices), x1=max(rogue_indices), fillcolor="orange", opacity=0.1, layer="below", line_width=0)
    
    fig.add_trace(go.Scatter(x=df.index, y=df["trade_freq"], mode="lines+markers", name="Trade Freq", line=dict(color="cyan", width=2)))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=30, b=20), xaxis_title="Data Point", yaxis_title="Requests/sec")
    st.plotly_chart(fig, use_container_width=True, key="trade_freq_chart")
else:
    st.warning("Waiting for telemetry data...")

st.markdown("---")

# --- EVENT SUMMARY ---
st.subheader("📌 Sentinel & Bot Event Sequence")

if events:
    # Show last 5 events in a clear sequence
    last_5_events = events[-5:]
    for idx, event in enumerate(last_5_events):
        event_type = event.get("event_type", "")
        action = event.get("action", "")
        message = event.get("message", "")
        event_time = event.get("timestamp")
        
        time_str = event_time.strftime('%H:%M:%S') if event_time else "N/A"
        
        if event_type == "BOT_COMMAND":
            if action == "FORCE_ROGUE":
                st.info(f"✅ [{time_str}] ROGUE MODE FORCED from dashboard")
            elif action == "KILL_SURE":
                st.error(f"💀 [{time_str}] BOT KILLED - Process received KILL_SURE command")
            elif action == "RESET_BOT":
                st.success(f"♻️ [{time_str}] BOT RESET - System returned to healthy mode")
        elif event_type == "ANOMALY_ACTION":
            if action == "KILL_SURE":
                st.error(f"🔥 [{time_str}] SENTINEL TRIGGERED KILL_SURE - Threshold breached by {event.get('raw_error', 'N/A')}")
            elif action == "SLOW_DOWN":
                st.warning(f"🐢 [{time_str}] SENTINEL ACTION: SLOW_DOWN - Anomaly detected")
        elif event_type == "CALIBRATION_COMPLETE":
            st.success(f"⚙️ [{time_str}] CALIBRATION COMPLETE - Threshold: {event.get('threshold', 'N/A')}")
        elif event_type == "SESSION_START":
            st.info(f"🌐 [{time_str}] NEW SESSION - Bot restarted")

st.markdown("---")

# --- EVENT TABLE ---
st.subheader("📝 Full System Event Log")
if events:
    df_events = pd.DataFrame(events)
    df_events["timestamp"] = df_events["timestamp"].dt.strftime("%H:%M:%S")
    display = df_events[["timestamp", "event_type", "action", "message", "raw_error", "action_delay"]]
    st.dataframe(display.tail(25).fillna(""), use_container_width=True)
else:
    st.info("No system events recorded yet.")

st.markdown("---")
st.caption("🔄 Auto-refreshing every second...")

# Refresh the page every 1 second
time.sleep(1)
st.rerun()

