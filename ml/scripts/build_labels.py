import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
from app.core.config import settings

def fetch_raw_data(limit=10000):
    """
    Fetches raw trip updates and vehicle positions from DB.
    For this MVP, we will simulate data if DB is empty.
    """
    # Real logic: Query rt_trip_updates_raw and join with gtfs static
    # Simulation for MVP:
    print("Generating synthetic data for training...")
    
    n_samples = 5000
    df = pd.DataFrame({
        'route_id': np.random.choice(['101', 'Red', 'Green', 'Blue'], n_samples),
        'stop_id': np.random.choice(['STOP_A', 'STOP_B', 'STOP_C', 'STOP_D'], n_samples),
        'hour_of_day': np.random.randint(6, 22, n_samples),
        'day_of_week': np.random.randint(0, 6, n_samples), # 0=Monday
        'is_weekend': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'stop_sequence': np.random.randint(1, 20, n_samples),
        'actual_delay_seconds': np.random.normal(loc=120, scale=300, size=n_samples) # Mean 2 min delay
    })
    
    # Target Label: late_5min (1 if delay >= 300s)
    df['late_5min'] = (df['actual_delay_seconds'] >= 300).astype(int)
    
    # Additional features to simulate reality
    # Rush hour (7-9, 16-18) -> higher delay
    mask_rush = df['hour_of_day'].isin([7, 8, 9, 16, 17, 18])
    df.loc[mask_rush, 'actual_delay_seconds'] += np.random.normal(180, 60, mask_rush.sum())
    
    # Recalculate target after modifying delay
    df['late_5min'] = (df['actual_delay_seconds'] >= 300).astype(int)
    
    return df

if __name__ == "__main__":
    df = fetch_raw_data()
    output_path = "ml/data/training_data.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} samples to {output_path}")
