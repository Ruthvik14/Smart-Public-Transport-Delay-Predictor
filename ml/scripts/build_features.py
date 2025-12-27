import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib
import os

def build_features():
    input_path = "ml/data/training_data.csv"
    if not os.path.exists(input_path):
        print("Data not found. Run build_labels.py first.")
        return

    df = pd.read_csv(input_path)
    
    # Features
    numeric_features = ['hour_of_day', 'day_of_week', 'is_weekend', 'stop_sequence']
    categorical_features = ['route_id'] # Stop ID might be too high cardinality for MVP, let's omit for now or hash
    
    X = df[numeric_features + categorical_features]
    y = df['late_5min']
    
    # Verify split (simulate time-based by splitting top/bottom if sorted, but data is random)
    # We'll just do random split for synthetic data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    return X_train, X_test, y_train, y_test, numeric_features, categorical_features

if __name__ == "__main__":
    build_features()
