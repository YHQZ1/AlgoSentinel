import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib 

def create_sequences(data, window_size=48): # Corrected to 48
    sequences = []
    for i in range(len(data) - window_size + 1):
        sequences.append(data[i : i + window_size])
    return np.array(sequences)

def preprocess_data():
    df = pd.read_csv("healthy_bot_data.csv")
    print(f"📦 Loaded {len(df)} samples.")

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)
    joblib.dump(scaler, "scaler.pkl")
    print("💾 Scaler saved as scaler.pkl")

    # FIXED: This MUST be 48 to match the model
    window_size = 48 
    sequences = create_sequences(scaled_data, window_size)
    
    print(f"✨ Processed data into {sequences.shape[0]} sequences of length {window_size}.")
    return sequences

if __name__ == "__main__":
    data = preprocess_data()
    np.save("train_sequences_v2.npy", data)
    print("✅ Training sequences saved as train_sequences_v2.npy")