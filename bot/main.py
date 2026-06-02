import asyncio
import os
import random
import time
import uuid

import redis.asyncio as redis

# Load config from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
COMMAND_CHANNEL = "bot_commands"
EVENT_STREAM = "system_events"

class MockTradingBot:
    def __init__(self):
        self.is_rogue = False
        self.killed = False
        self.mode = "HEALTHY"
        self.redis_client = None
        self.session_id = uuid.uuid4().hex

    async def connect_redis(self):
        self.redis_client = await redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        print("✅ Connected to Redis Stream")
        print(f"🔑 Bot session id: {self.session_id}")

    async def log_system_event(self, event_type, message, extra_fields=None):
        fields = {
            "event_type": event_type,
            "message": message,
            "session_id": self.session_id,
            "timestamp": str(time.time())
        }
        if extra_fields:
            fields.update({k: str(v) for k, v in extra_fields.items()})
        await self.redis_client.xadd(EVENT_STREAM, fields)

    async def get_market_metrics(self):
        """Simulates the 'Vital Signs' of the bot's activity"""
        if self.killed:
            return {
                "trade_freq": 0.0,
                "volatility": 0.0,
                "order_cancel_rate": 0.0,
                "latency": 0.0
            }

        if not self.is_rogue:
            return {
                "trade_freq": random.uniform(0.1, 0.5),
                "volatility": random.uniform(0.01, 0.02),
                "order_cancel_rate": random.uniform(0.05, 0.15),
                "latency": random.uniform(0.001, 0.005)
            }

        # Rogue mode should produce clear anomaly behavior for the sentinel to act on.
        return {
            "trade_freq": random.uniform(60.0, 120.0),
            "volatility": random.uniform(0.30, 0.75),
            "order_cancel_rate": random.uniform(0.75, 0.99),
            "latency": random.uniform(0.02, 0.10)
        }

    async def run_trading_loop(self):
        """The main trading loop."""
        print("🚀 Trading Bot Started...")
        while True:
            metrics = await self.get_market_metrics()
            metrics["session_id"] = self.session_id
            metrics["mode"] = "KILLED" if self.killed else ("ROGUE" if self.is_rogue else "HEALTHY")
            await self.send_log(metrics)
            await asyncio.sleep(0.1)

    async def send_log(self, metrics):
        """Sends the telemetry data to the Redis Stream"""
        try:
            await self.redis_client.xadd("bot_telemetry", metrics)
        except Exception as e:
            print(f"❌ Log Error: {e}")

    async def listen_for_commands(self):
        """LISTENS for signals from the AI Sentinel"""
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(COMMAND_CHANNEL)
        print("👂 Listening for Sentinel commands...")
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                command = message['data']
                print(f"\n⚠️ RECEIVED COMMAND: {command}")
                if command == "KILL_SURE":
                    self.killed = True
                    self.is_rogue = False
                    await self.log_system_event("BOT_COMMAND", "Received KILL_SURE from sentinel", {"command": command})
                    print("💀 SYSTEM TERMINATED BY SENTINEL. ENTERING KILLED STATE.")
                elif command == "FLATTEN_POSITIONS":
                    await self.log_system_event("BOT_COMMAND", "Received FLATTEN_POSITIONS from sentinel", {"command": command})
                    print("📉 FLATTENING ALL POSITIONS... returning to cash.")
                elif command == "SLOW_DOWN":
                    await self.log_system_event("BOT_COMMAND", "Received SLOW_DOWN from sentinel", {"command": command})
                    print("🐢 SLOWING DOWN trading frequency...")
                elif command == "FORCE_ROGUE":
                    self.killed = False
                    self.is_rogue = True
                    await self.log_system_event("BOT_COMMAND", "Received FORCE_ROGUE from dashboard", {"command": command})
                    print("🚨 Rogue mode forced by dashboard.")
                elif command == "RESET_BOT":
                    self.killed = False
                    self.is_rogue = False
                    self.session_id = uuid.uuid4().hex
                    await self.log_system_event("BOT_COMMAND", "Received RESET_BOT from dashboard", {"command": command})
                    print("♻️ Bot reset successfully. New session started.")

    async def toggle_rogue_mode(self):
        """Disabled: Do not auto-toggle. Only change via commands."""
        await asyncio.sleep(999999)  # Sleep forever, never trigger

async def main():
    bot = MockTradingBot()
    await bot.connect_redis()
    
    # Run the trading loop, the mode-toggler, and the command listener concurrently
    await asyncio.gather(
        bot.run_trading_loop(),
        bot.toggle_rogue_mode(),
        bot.listen_for_commands()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping Bot...")