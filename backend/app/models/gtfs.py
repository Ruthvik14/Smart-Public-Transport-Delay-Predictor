from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.db.session import Base

class Stop(Base):
    __tablename__ = "stops"
    stop_id = Column(String, primary_key=True, index=True)
    stop_code = Column(String, nullable=True)
    stop_name = Column(String, nullable=False)
    stop_desc = Column(String, nullable=True)
    stop_lat = Column(Float, nullable=False)
    stop_lon = Column(Float, nullable=False)
    geom = Column(Geometry('POINT', srid=4326))

class Route(Base):
    __tablename__ = "routes"
    route_id = Column(String, primary_key=True, index=True)
    route_short_name = Column(String, nullable=True)
    route_long_name = Column(String, nullable=True)
    route_type = Column(Integer, nullable=True)
    route_color = Column(String, nullable=True)
    route_text_color = Column(String, nullable=True)

class Trip(Base):
    __tablename__ = "trips"
    trip_id = Column(String, primary_key=True, index=True)
    route_id = Column(String, ForeignKey("routes.route_id"), index=True)
    service_id = Column(String, index=True)
    trip_headsign = Column(String, nullable=True)
    direction_id = Column(Integer, nullable=True)
    shape_id = Column(String, nullable=True)

    route = relationship("Route")

class StopTime(Base):
    __tablename__ = "stop_times"
    trip_id = Column(String, ForeignKey("trips.trip_id"), primary_key=True)
    stop_id = Column(String, ForeignKey("stops.stop_id"), primary_key=True)
    stop_sequence = Column(Integer, primary_key=True)
    arrival_time = Column(String, nullable=True) # Text in GTFS (HH:MM:SS)
    departure_time = Column(String, nullable=True)
    
    trip = relationship("Trip")
    stop = relationship("Stop")
