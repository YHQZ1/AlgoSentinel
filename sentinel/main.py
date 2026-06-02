import asyncio
import os
import socket
import time
from collections import deque

import joblib
import numpy as np
import pandas as pd
import redis.asyncio as redis
from redis import exceptions as redis_exceptions
import torch
import torch.nn as nn

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
STREAM_NAME = "bot_telemetry"
COMMAND_CHANNEL = "bot_commands"
EVENT_STREAM = "system_events"
STREAM_GROUP = "sentinel_group"
CONSUMER_NAME = f"sentinel_{socket.gethostname()}"
WINDOW_SIZE = 48
CALIBRATION_SAMPLES = 60
ERROR_SMOOTHING_ALPHA = 0.30
CONSECUTIVE_ALERTS_TO_TRIGGER = 2
ALERT_COOLDOWN_SECONDS = 5.0
MIN_THRESHOLD = 0.05

# The architecture must match training exactly.
class TCNAutoencoder(nn.Module):
    def __init__(self, input_dim, sequence_length):
        super(TCNAutoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv1d(input_dim, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Dropout(0.1),
            nn.Conv1d(16, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2)
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(8, 16, kernel_size=2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose1d(16, input_dim, kernel_size=2, stride=2)
        )

    def forward(self, x):
        x = x.permute(0, 2, 1)
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded.permute(0, 2, 1)

class AISentinel:
    def __init__(self):
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.redis_client = None
        self.model = None
        self.scaler = None
        self.buffer = deque(maxlen=WINDOW_SIZE)
        self.threshold = None
        self.smoothed_error = None
        self.consecutive_alerts = 0
        self.last_trigger_at = 0.0
        self.first_alert_time = None
        self.session_id = None
        self.warmup_errors = []

    async def setup(self):
        self.redis_client = await redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        self.scaler = joblib.load("/app/scaler.pkl")

        self.model = TCNAutoencoder(input_dim=4, sequence_length=WINDOW_SIZE).to(self.device)
        self.model.load_state_dict(torch.load("/app/sentinel_model.pth", map_location=self.device))
        self.model.eval()

        await self._ensure_consumer_group()
        print("🧠 Sentinel loaded and ready. Awaiting fresh telemetry...")

    async def _ensure_consumer_group(self):
        try:
            await self.redis_client.xgroup_create(STREAM_NAME, STREAM_GROUP, id="$", mkstream=True)
        except redis_exceptions.ResponseError as exc:
            if "BUSYGROUP" in str(exc):
                await self.redis_client.xgroup_setid(STREAM_NAME, STREAM_GROUP, "$")
            else:
                raise

    async def log_system_event(self, event_type, message, extra_fields=None):
        fields = {
            "event_type": event_type,
            "message": message,
            "session_id": self.session_id or "unknown",
            "timestamp": str(time.time())
        }
        if extra_fields:
            fields.update({k: str(v) for k, v in extra_fields.items()})
        await self.redis_client.xadd(EVENT_STREAM, fields)

    def _reset_session_state(self):
        self.buffer.clear()
        self.smoothed_error = None
        self.consecutive_alerts = 0
        self.last_trigger_at = 0.0
        self.first_alert_time = None

    async def _is_current_session(self, content):
        session_id = content.get("session_id")
        if session_id is None:
            return self.session_id is None

        if self.session_id is None:
            self.session_id = session_id
            self._reset_session_state()
            print(f"🌐 New bot session detected: {self.session_id}")
            await self.log_system_event("SESSION_START", f"New bot session {self.session_id} started")
            return True

        if session_id != self.session_id:
            print(f"🔄 Bot session changed from {self.session_id} to {session_id}; resetting sentinel state")
            self.session_id = session_id
            self._reset_session_state()
            await self.log_system_event("SESSION_CHANGE", f"Bot session changed to {self.session_id}")

        return True

    async def analyze_behavior(self, sequence):
        df_seq = pd.DataFrame(sequence, columns=['trade_freq', 'volatility', 'order_cancel_rate', 'latency'])
        scaled_seq = self.scaler.transform(df_seq)
        tensor_seq = torch.tensor(scaled_seq, dtype=torch.float32).unsqueeze(0).to(self.device)

        with torch.no_grad():
            reconstruction = self.model(tensor_seq)
            loss = torch.mean((tensor_seq - reconstruction) ** 2).item()

        return loss

    async def calibrate_threshold(self):
        print("⏳ Calibrating threshold from healthy warmup samples...")

        while len(self.warmup_errors) < CALIBRATION_SAMPLES:
            messages = await self.redis_client.xreadgroup(STREAM_GROUP, CONSUMER_NAME, {STREAM_NAME: ">"}, count=1, block=2000)
            if not messages:
                continue

            for _, entries in messages:
                for msg_id, content in entries:
                    if not await self._is_current_session(content):
                        await self.redis_client.xack(STREAM_NAME, STREAM_GROUP, msg_id)
                        continue

                    values = [float(content[k]) for k in ['trade_freq', 'volatility', 'order_cancel_rate', 'latency']]
                    self.buffer.append(values)

                    if len(self.buffer) == WINDOW_SIZE:
                        error = await self.analyze_behavior(list(self.buffer))
                        self.warmup_errors.append(error)
                        if len(self.warmup_errors) % 20 == 0:
                            print(f"  • Calibrated {len(self.warmup_errors)}/{CALIBRATION_SAMPLES} windows")

                    await self.redis_client.xack(STREAM_NAME, STREAM_GROUP, msg_id)

        self.threshold = max(MIN_THRESHOLD, float(np.percentile(self.warmup_errors, 95)))
        await self.log_system_event("CALIBRATION_COMPLETE", "Threshold calibration completed", {"threshold": self.threshold, "sample_count": CALIBRATION_SAMPLES})
        print(f"✅ Calibration complete. Anomaly threshold = {self.threshold:.4f}")

    async def run(self):
        await self.setup()
        await self.calibrate_threshold()
        self.buffer.clear()
        print("📡 Monitoring Bot Telemetry with session-aware Redis stream consumption...")

        while True:
            messages = await self.redis_client.xreadgroup(STREAM_GROUP, CONSUMER_NAME, {STREAM_NAME: ">"}, count=1, block=1000)
            if not messages:
                continue

            for _, entries in messages:
                for msg_id, content in entries:
                    if not await self._is_current_session(content):
                        await self.redis_client.xack(STREAM_NAME, STREAM_GROUP, msg_id)
                        continue

                    values = [float(content[k]) for k in ['trade_freq', 'volatility', 'order_cancel_rate', 'latency']]
                    self.buffer.append(values)

                    if len(self.buffer) == WINDOW_SIZE:
                        error = await self.analyze_behavior(list(self.buffer))
                        self.smoothed_error = error if self.smoothed_error is None else ERROR_SMOOTHING_ALPHA * error + (1 - ERROR_SMOOTHING_ALPHA) * self.smoothed_error
                        is_rogue_mode = content.get("mode") == "ROGUE"

                        if error <= self.threshold and not is_rogue_mode:
                            print(f"✅ Healthy | raw={error:.4f} | smooth={self.smoothed_error:.4f} | threshold={self.threshold:.4f}", end="\r")
                            self.consecutive_alerts = 0
                            self.first_alert_time = None
                        else:
                            self.consecutive_alerts += 1
                            if self.first_alert_time is None:
                                self.first_alert_time = time.time()

                            print(f"\n⚠️  Alert {self.consecutive_alerts}/{CONSECUTIVE_ALERTS_TO_TRIGGER} | raw={error:.4f} | smooth={self.smoothed_error:.4f}")

                            if ((is_rogue_mode and self.consecutive_alerts >= 1) or
                                (self.consecutive_alerts >= CONSECUTIVE_ALERTS_TO_TRIGGER)) and \
                                (time.time() - self.last_trigger_at) > ALERT_COOLDOWN_SECONDS:
                                await self.trigger_kill_switch(error, force_kill=is_rogue_mode)
                                self.last_trigger_at = time.time()

                    await self.redis_client.xack(STREAM_NAME, STREAM_GROUP, msg_id)

    async def trigger_kill_switch(self, error, force_kill=False):
        if force_kill:
            msg = "KILL_SURE"
        elif self.smoothed_error > self.threshold * 3:
            msg = "KILL_SURE"
        elif self.smoothed_error > self.threshold * 1.5:
            msg = "FLATTEN_POSITIONS"
        else:
            msg = "SLOW_DOWN"

        action_delay = 0.0
        if self.first_alert_time is not None:
            action_delay = time.time() - self.first_alert_time

        event_payload = {
            "action": msg,
            "raw_error": f"{error:.4f}",
            "smoothed_error": f"{self.smoothed_error:.4f}",
            "threshold": f"{self.threshold:.4f}",
            "consecutive_alerts": self.consecutive_alerts,
            "action_delay": f"{action_delay:.3f}",
            "force_kill": str(force_kill)
        }

        print(f"\n💥 PANIC PROTOCOL: {msg} | raw={error:.4f} | smooth={self.smoothed_error:.4f}")
        await self.log_system_event("ANOMALY_ACTION", f"Sentinel triggered {msg}", event_payload)
        await self.redis_client.publish(COMMAND_CHANNEL, msg)
        self.first_alert_time = None

async def main():
    sentinel = AISentinel()
    await sentinel.run()

if __name__ == "__main__":
    asyncio.run(main())