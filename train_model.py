import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import DataLoader, TensorDataset

# 1. Hardware Setup (Device Agnostic)
device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
print(f"🚀 Training on: {device}")

# 2. The TCN Autoencoder Architecture
class TCNAutoencoder(nn.Module):
    def __init__(self, input_dim, sequence_length):
        super(TCNAutoencoder, self).__init__()
        
        # ENCODER: Compresses the sequence
        self.encoder = nn.Sequential(
            nn.Conv1d(input_dim, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2), 
            nn.Dropout(0.1), 
            nn.Conv1d(16, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2)  
        )
        
        # DECODER: Rebuilds the sequence
        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(8, 16, kernel_size=2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose1d(16, input_dim, kernel_size=2, stride=2),
            # REMOVED Sigmoid() -> We now use Linear output to allow errors to explode
        )

    def forward(self, x):
        # PyTorch Conv1d expects: (Batch, Features, Sequence_Length)
        x = x.permute(0, 2, 1) 
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        # Switch back to: (Batch, Sequence_Length, Features)
        return decoded.permute(0, 2, 1)

# 3. Training Logic
def train():
    try:
        data = np.load("train_sequences_v2.npy")
    except FileNotFoundError:
        print("❌ Error: train_sequences_v2.npy not found. Run preprocess.py first!")
        return

    print(f"DEBUG: Data shape is {data.shape}") 
    
    # IMPORTANT: We no longer normalize to 0-1. 
    # We train directly on the StandardScaler outputs (Z-scores).
    X = torch.tensor(data, dtype=torch.float32).to(device)
    dataset = TensorDataset(X, X) 
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    model = TCNAutoencoder(input_dim=4, sequence_length=48).to(device)
    criterion = nn.MSELoss() 
    optimizer = optim.Adam(model.parameters(), lr=0.0005)

    print("🧠 Training started...!")
    for epoch in range(100):
        total_loss = 0
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            output = model(batch_x)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/100 | Loss: {total_loss/len(loader):.6f}")

    torch.save(model.state_dict(), "sentinel_model.pth")
    print("✅ Model saved as sentinel_model.pth")

if __name__ == "__main__":
    train()