from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import SessionLocal
from app.models.gtfs import Stop, Route
from app.schemas.gtfs import StopSchema, RouteSchema # Need to create schemas
from geoalchemy2.functions import ST_DWithin, ST_Distance
from geoalchemy2.elements import WKTElement

router = APIRouter()

import redis
import json
from app.core.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

@router.get("/vehicles")
def get_vehicles():
    """Get all active vehicles from Redis."""
    keys = redis_client.keys("vehicle:*")
    if not keys:
        return []
    
    # MGET is faster than loop
    vehicles_json = redis_client.mget(keys)
    vehicles = [json.loads(v) for v in vehicles_json if v]
    return vehicles

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stops/search", response_model=List[StopSchema])
def search_stops(q: str, db: Session = Depends(get_db)):
    """Search stops by name."""
    return db.query(Stop).filter(Stop.stop_name.ilike(f"%{q}%")).limit(10).all()

@router.get("/stops/nearby", response_model=List[StopSchema])
def get_nearby_stops(lat: float, lon: float, radius: float = 0.01, db: Session = Depends(get_db)):
    """Find stops within radius (approx degrees for now, better use meters with geography)."""
    # Using simple ST_DWithin with geometry (degrees) for simplicity in this MVP
    # In production, cast to geography or use a projected CRS for meters.
    # 0.01 degrees is roughly 1km.
    
    point = WKTElement(f'POINT({lon} {lat})', srid=4326)
    return db.query(Stop).filter(ST_DWithin(Stop.geom, point, radius)).limit(20).all()

@router.get("/stops/{stop_id}", response_model=StopSchema)
def get_stop(stop_id: str, db: Session = Depends(get_db)):
    stop = db.query(Stop).filter(Stop.stop_id == stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    return stop

@router.get("/routes", response_model=List[RouteSchema])
def get_routes(db: Session = Depends(get_db)):
    """List all routes."""
    return db.query(Route).all()

@router.get("/routes/{route_id}", response_model=RouteSchema)
def get_route(route_id: str, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.route_id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route
