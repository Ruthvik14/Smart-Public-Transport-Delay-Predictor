from .endpoints import router, get_db
from app.api import endpoints
import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.gtfs import ArrivalSchema
from app.models.gtfs import StopTime, Trip
from app.services.gtfs_rt import parse_trip_updates
from app.services.prediction import prediction_service
import redis
import json
from app.core.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

@endpoints.router.get("/stops/{stop_id}/arrivals", response_model=list[ArrivalSchema])
def get_stop_arrivals(stop_id: str, db: Session = Depends(get_db)):
    """
    Get upcoming arrivals for a stop.
    Merges Static Schedule with Real-time Trip Updates + ML Predictions.
    """
    # 1. Get Scheduled Arrivals for next 60 mins (Simplified to limit 50 limit)
    stop_times = db.query(StopTime).filter(StopTime.stop_id == stop_id).join(Trip).limit(50).all()
    
    arrivals = []
    
    for st in stop_times:
        trip_id = st.trip_id
        route_id = st.trip.route_id
        
        # Redis Key: trip_update:{trip_id}
        tu_data = redis_client.get(f"trip_update:{trip_id}")
        
        pred_arrival = None
        delay = 0.0
        status = "SCHEDULED"
        prob_late = 0.0
        
        if tu_data:
            tu = json.loads(tu_data)
            # Find update for this stop sequence
            for update in tu['stop_time_updates']:
                if update['stop_sequence'] == st.stop_sequence:
                    if update.get('arrival_delay'):
                         delay = float(update['arrival_delay'] / 60.0) # minutes
                         status = "LATE" if delay > 5 else "ON_TIME"
                         if delay < -1: status = "EARLY"
                         break
        
        # ML Prediction Section
        # Build features for specific trip/stop
        features = {
            'route_id': route_id,
            'stop_sequence': st.stop_sequence,
            # Simple heuristic for time features since we don't have parsed 'arrival_time' handy as datetime
            # In real app, we convert st.arrival_time (string) to datetime
            'hour_of_day': 12, # Placeholder
            'day_of_week': 2, # Placeholder
            'is_weekend': 0
        }
        
        prediction = prediction_service.predict(features)
        prob_late = prediction['probability_late_5min']
        
        arrivals.append(ArrivalSchema(
            trip_id=trip_id,
            route_id=route_id,
            headsign=st.trip.trip_headsign,
            scheduled_arrival=st.arrival_time,
            predicted_arrival=None, 
            delay_minutes=delay,
            status=status,
            probability_late_5min=prob_late,
            vehicle_id=None
        ))
        
    return arrivals
