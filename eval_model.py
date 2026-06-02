import torch
import torch.nn as nn
import numpy as np
import joblib
import pandas as pd
import random

# Hardware
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

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
            nn.ConvTranspose1d(16, input_dim, kernel_size=2, stride=2),
        )

    def forward(self, x):
        x = x.permute(0, 2, 1)
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded.permute(0, 2, 1)

def get_error(model, scaler, sequence):
    # 1. Convert to DataFrame and scale
    df = pd.DataFrame(sequence, columns=['trade_freq', 'volatility', 'order_cancel_rate', 'latency'])
    scaled = scaler.transform(df)
    
    # 2. No more 0-1 normalization. Use raw scaled values.
    tensor = torch.tensor(scaled, dtype=torch.float32).unsqueeze(0).to(device)
    
    with torch.no_grad():
        reconstruction = model(tensor)
        loss = torch.mean((tensor - reconstruction)**2).item()
    return loss

def evaluate():
    # 1. Load everything
    try:
        scaler = joblib.load("scaler.pkl")
        model = TCNAutoencoder(input_dim=4, sequence_length=48).to(device)
        model.load_state_dict(torch.load("sentinel_model.pth", map_location=device))
        model.eval()
    except FileNotFoundError:
        print("❌ Error: Required files (scaler.pkl or sentinel_model.pth) not found!")
        return

    # 2. Create a "Healthy" Sample (Low values)
    healthy_sample = np.random.uniform(0.1, 0.5, (48, 4))
    
    # 3. Create a "Rogue" Sample (High values + ERRATIC SPIKES)
    rogue_sample = np.random.uniform(5.0, 20.0, (48, 4))
    for _ in range(15): # Inject extreme spikes
        rogue_sample[random.randint(0, 47), random.randint(0, 3)] = 100.0 

    # 4. Calculate Errors
    h_error = get_error(model, scaler, healthy_sample)
    r_error = get_error(model, scaler, rogue_sample)

    print("\n" + "="*30)
    print(f"📊 EVALUATION RESULTS")
    print("="*30)
    print(f"Healthy Sample Error: {h_error:.6f}")
    print(f"Rogue Sample Error:   {r_error:.6f}")
    print("-" * 30)
    print(f"Ratio (Rogue/Healthy): {r_error/h_error:.2f}x")
    print("="*30)

    if r_error > h_error * 5: # Increased threshold for a "Strong" model
        print("✅ CONCLUSION: The model successfully distinguishes between states!")
    else:
        print("⚠️ CONCLUSION: The model is still too similar. Try more epochs or different data.")

if __name__ == "__main__":
    evaluate()