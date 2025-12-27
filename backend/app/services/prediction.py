import joblib
import pandas as pd
import os
from app.schemas.gtfs import ArrivalSchema

MODEL_PATH = "/ml/models/delay_predictor_v1.joblib"
# In Docker, /ml is volume mounted.

class PredictionService:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                print(f"Loaded model from {MODEL_PATH}")
            except Exception as e:
                print(f"Failed to load model: {e}")
        else:
            print(f"Model not found at {MODEL_PATH}. Prediction service will assume 0 delay.")

    def predict(self, features: dict) -> dict:
        """
        Returns {'probability_late_5min': float, 'predicted_delay': float}
        """
        if not self.model:
            return {'probability_late_5min': 0.0, 'predicted_delay': 0.0}
        
        # Convert features to DataFrame
        df = pd.DataFrame([features])
        
        try:
            prob = self.model.predict_proba(df)[:, 1][0]
            # Simple regression Proxy: prob * 10 mins? Or just use binary for now.
            # Better: Train a regressor. For MVP, we only promised late_5min.
            # We can approximate delay as: if prob > 0.8: 5 mins, else 0.
            # Or use expected value if we had a distribution.
            
            return {
                'probability_late_5min': float(prob),
                'predicted_delay': 0.0 # Placeholder
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            return {'probability_late_5min': 0.0, 'predicted_delay': 0.0}

prediction_service = PredictionService()
