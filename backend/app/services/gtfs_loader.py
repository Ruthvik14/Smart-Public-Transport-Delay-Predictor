import os
import zipfile
import pandas as pd
import requests
from io import BytesIO
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.gtfs import Stop, Route, Trip, StopTime, Base

GTFS_URL = "https://rideconnecttransit.com/gtfs"

def download_gtfs():
    print(f"Downloading GTFS from {GTFS_URL}...")
    response = requests.get(GTFS_URL)
    response.raise_for_status()
    return BytesIO(response.content)

def load_gtfs_static():
    print("Initializing DB tables...")
    Base.metadata.create_all(bind=engine)
    
    gtfs_zip = download_gtfs()
    
    with zipfile.ZipFile(gtfs_zip) as z:
        print("Loading routes...")
        with z.open("routes.txt") as f:
            routes_df = pd.read_csv(f)
            routes_df = routes_df.fillna("")
            
        print("Loading stops...")
        with z.open("stops.txt") as f:
            stops_df = pd.read_csv(f)
            stops_df = stops_df.fillna("")

        print("Loading trips...")
        with z.open("trips.txt") as f:
            trips_df = pd.read_csv(f)
            trips_df = trips_df.fillna("")

        print("Loading stop_times (this might take a while)...")
        with z.open("stop_times.txt") as f:
            stop_times_df = pd.read_csv(f)
            stop_times_df = stop_times_df.fillna("")

    db: Session = SessionLocal()
    try:
        # Load Routes
        print(f"Inserting {len(routes_df)} routes...")
        for _, row in routes_df.iterrows():
            route = Route(
                route_id=str(row['route_id']),
                route_short_name=row.get('route_short_name'),
                route_long_name=row.get('route_long_name'),
                route_type=row.get('route_type'),
                route_color=row.get('route_color'),
                route_text_color=row.get('route_text_color')
            )
            db.merge(route)
        
        # Load Stops
        print(f"Inserting {len(stops_df)} stops...")
        for _, row in stops_df.iterrows():
            # Create Point geometry: SRID 4326 is WGS84
            geom = f"POINT({row['stop_lon']} {row['stop_lat']})"
            stop = Stop(
                stop_id=str(row['stop_id']),
                stop_code=str(row.get('stop_code', '')),
                stop_name=row['stop_name'],
                stop_desc=row.get('stop_desc'),
                stop_lat=row['stop_lat'],
                stop_lon=row['stop_lon'],
                geom=geom
            )
            db.merge(stop)

        db.commit()

        # Load Trips
        print(f"Inserting {len(trips_df)} trips...")
        # Bulk Insert might be faster, but let's stick to simple upsert for now or delete all first
        # For simplicity in this script, we'll iterate. Production should use bulk_save_objects
        
        # Clean existing Data for idempotency if needed (optional)
        # db.query(Trip).delete()
        # db.query(StopTime).delete()
        
        trips_to_insert = []
        for _, row in trips_df.iterrows():
            trips_to_insert.append(Trip(
                trip_id=str(row['trip_id']),
                route_id=str(row['route_id']),
                service_id=str(row['service_id']),
                trip_headsign=row.get('trip_headsign'),
                direction_id=row.get('direction_id'),
                shape_id=str(row.get('shape_id', ''))
            ))
        
        # Determine chunk size for bulk insert
        chunk_size = 1000
        for i in range(0, len(trips_to_insert), chunk_size):
            db.bulk_save_objects(trips_to_insert[i:i+chunk_size])
            db.commit()
            
        # Load Stop Times (Large)
        print(f"Inserting {len(stop_times_df)} stop_times...")
        stop_times_to_insert = []
        for _, row in stop_times_df.iterrows():
            stop_times_to_insert.append(StopTime(
                trip_id=str(row['trip_id']),
                stop_id=str(row['stop_id']),
                stop_sequence=int(row['stop_sequence']),
                arrival_time=row.get('arrival_time'),
                departure_time=row.get('departure_time')
            ))
            
            if len(stop_times_to_insert) >= 5000:
                db.bulk_save_objects(stop_times_to_insert)
                db.commit()
                stop_times_to_insert = []
        
        if stop_times_to_insert:
            db.bulk_save_objects(stop_times_to_insert)
            db.commit()

        print("GTFS Static Load Complete!")
        
    except Exception as e:
        print(f"Error loading GTFS: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_gtfs_static()
