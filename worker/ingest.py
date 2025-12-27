from celery.schedules import crontab
from tasks import app
from app.services.gtfs_rt import fetch_feed, parse_vehicle_positions, parse_trip_updates, VEHICLE_POSITIONS_URL, TRIP_UPDATES_URL
from app.core.config import settings
import redis
import json

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Poll Vehicle Positions every 10 seconds
    sender.add_periodic_task(10.0, ingest_vehicle_positions.s(), name='ingest-vehicles-10s')
    
    # Poll Trip Updates every 10 seconds
    sender.add_periodic_task(10.0, ingest_trip_updates.s(), name='ingest-trips-10s')

@app.task
def ingest_vehicle_positions():
    print("Fetching Vehicle Positions...")
    feed = fetch_feed(VEHICLE_POSITIONS_URL)
    vehicles = parse_vehicle_positions(feed)
    
    if not vehicles:
        return "No vehicles found"

    # Pipeline Redis updates for performance
    pipe = redis_client.pipeline()
    
    for v in vehicles:
        # Cache latest state per vehicle
        # Key: vehicle:{vehicle_id}
        key = f"vehicle:{v['vehicle_id']}"
        pipe.set(key, json.dumps(v), ex=600) # Expire after 10 mins if no update
        
        # Also store by route for quick lookup
        # Key: route_vehicles:{route_id} -> Set of vehicle IDs
        # We need to manage this set carefully (remove if vehicle changes route)
        # For MVP simple expiration might be enough or just scan. 
        # Better: valid_vehicles:{route_id} list
    
    pipe.execute()
    
    # Telemetry / DB Archival would go here (omitted for MVP speed)
    return f"Ingested {len(vehicles)} vehicles"

@app.task
def ingest_trip_updates():
    print("Fetching Trip Updates...")
    feed = fetch_feed(TRIP_UPDATES_URL)
    updates = parse_trip_updates(feed)
    
    if not updates:
        return "No updates found"
        
    pipe = redis_client.pipeline()
    
    for u in updates:
        # Cache trip update
        # Key: trip_update:{trip_id}
        key = f"trip_update:{u['trip_id']}"
        pipe.set(key, json.dumps(u), ex=600)
        
    pipe.execute()
    return f"Ingested {len(updates)} trip updates"
