from pydantic import BaseModel
from typing import Optional, List

class StopBase(BaseModel):
    stop_id: str
    stop_name: str
    stop_lat: float
    stop_lon: float

class StopSchema(StopBase):
    stop_code: Optional[str] = None
    stop_desc: Optional[str] = None
    
    class Config:
        from_attributes = True

class RouteBase(BaseModel):
    route_id: str
    route_short_name: Optional[str]
    route_long_name: Optional[str]
    route_color: Optional[str]
    route_text_color: Optional[str]

class RouteSchema(RouteBase):
    route_type: Optional[int]
    
    class Config:
        from_attributes = True

class ArrivalSchema(BaseModel):
    trip_id: str
    route_id: str
    headsign: Optional[str]
    scheduled_arrival: str # HH:MM:SS
    predicted_arrival: Optional[str] # HH:MM:SS or ISO
    delay_minutes: Optional[float]
    status: str # "ON_TIME", "LATE", "EARLY", "SCHEDULED"
    probability_late_5min: Optional[float]
    vehicle_id: Optional[str]
