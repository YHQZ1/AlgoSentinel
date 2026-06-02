import redis
import pandas as pd
import time

REDIS_HOST = "localhost" 
REDIS_PORT = 6379
STREAM_NAME = "bot_telemetry"
SAMPLES_NEEDED = 5000 

def collect_healthy_data():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    print(f"⏳ Collecting {SAMPLES_NEEDED} PURELY healthy samples...")
    
    data = []
    last_id = '0-0'
    
    while len(data) < SAMPLES_NEEDED:
        messages = r.xread({STREAM_NAME: last_id}, count=10, block=1000)
        
        if messages:
            for stream, msgs in messages:
                for msg_id, content in msgs:
                    # --- THE SMART FILTER ---
                    # Only collect if trade_freq is low (Healthy range: 0.1 to 0.5)
                    # This ensures our 'Baseline' is not contaminated by Rogue data
                    if float(content['trade_freq']) < 1.0: 
                        data.append(content)
                    last_id = msg_id
            
            print(f"📈 Pure Healthy Samples: {len(data)}/{SAMPLES_NEEDED}...", end="\r")
            
    df = pd.DataFrame(data).astype(float)
    df.to_csv("healthy_bot_data.csv", index=False)
    print("\n✅ Pure Dataset Collected! Saved to healthy_bot_data.csv")

if __name__ == "__main__":
    collect_healthy_data()