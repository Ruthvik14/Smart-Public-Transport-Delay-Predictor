from google.transit import gtfs_realtime_pb2
import requests

# Feed URLs
VEHICLE_POSITIONS_URL = "https://rideconnecttransit.com/gtfs-rt/vehiclepositions"
TRIP_UPDATES_URL = "https://rideconnecttransit.com/gtfs-rt/tripupdates"
ALERTS_URL = "https://rideconnecttransit.com/gtfs-rt/alerts"

def fetch_feed(url: str):
    """Fetches and parses a GTFS-RT feed."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed
    except Exception as e:
        print(f"Error fetching feed {url}: {e}")
        return None

def parse_vehicle_positions(feed):
    vehicles = []
    if not feed:
        return vehicles
        
    for entity in feed.entity:
        if entity.HasField('vehicle'):
            v = entity.vehicle
            vehicles.append({
                'id': entity.id,
                'trip_id': v.trip.trip_id,
                'route_id': v.trip.route_id,
                'lat': v.position.latitude,
                'lon': v.position.longitude,
                'bearing': v.position.bearing,
                'speed': v.position.speed,
                'timestamp': v.timestamp,
                'vehicle_id': v.vehicle.id,
                'stop_id': v.stop_id,
                'current_status': v.current_status
            })
    return vehicles

def parse_trip_updates(feed):
    updates = []
    if not feed:
        return updates
        
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            tu = entity.trip_update
            stop_time_updates = []
            for stu in tu.stop_time_update:
                stop_time_updates.append({
                    'stop_sequence': stu.stop_sequence,
                    'stop_id': stu.stop_id,
                    'arrival_delay': stu.arrival.delay,
                    'arrival_time': stu.arrival.time,
                    'departure_delay': stu.departure.delay,
                    'departure_time': stu.departure.time
                })
            
            updates.append({
                'id': entity.id,
                'trip_id': tu.trip.trip_id,
                'route_id': tu.trip.route_id,
                'vehicle_id': tu.vehicle.id,
                'timestamp': tu.timestamp,
                'stop_time_updates': stop_time_updates
            })
    return updates
