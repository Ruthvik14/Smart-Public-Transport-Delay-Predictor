from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.gtfs import Stop, Route, Trip
from app.models.alerts import AlertSubscription, NotificationEvent
from app.services.gtfs_rt import parse_vehicle_positions, fetch_feed, VEHICLE_POSITIONS_URL
import redis
from app.core.config import settings

router = APIRouter()
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/admin/health")
def get_system_health():
    """Returns basic system health metrics."""
    # Check simple connectivity
    db_status = "ok"
    try:
        # Simple DB ping
        get_db().__next__().execute("SELECT 1")
    except:
        db_status = "error"
        
    redis_status = "ok"
    try:
        redis_client.ping()
    except:
        redis_status = "error"
        
    return {
        "database": db_status,
        "redis": redis_status,
        "worker": "active" # Assumption for MVP
    }

@router.get("/admin/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """Returns high-level analytics."""
    stop_count = db.query(Stop).count()
    route_count = db.query(Route).count()
    trip_count = db.query(Trip).count()
    sub_count = db.query(AlertSubscription).count()
    alert_count = db.query(NotificationEvent).count()
    
    # Live vehicles (from Redis cache or fetch fresh)
    # We can estimate from fetching feed or counting keys?
    # Fetching feed is easier for "right now" accuracy without scanning keys
    vehicles_live = 0
    try:
        feed = fetch_feed(VEHICLE_POSITIONS_URL)
        vehicles = parse_vehicle_positions(feed)
        vehicles_live = len(vehicles)
    except:
        pass
        
    return {
        "counts": {
            "stops": stop_count,
            "routes": route_count,
            "trips": trip_count
        },
        "engagement": {
            "subscriptions": sub_count,
            "alerts_triggered": alert_count
        },
        "realtime": {
            "active_vehicles": vehicles_live
        }
    }
