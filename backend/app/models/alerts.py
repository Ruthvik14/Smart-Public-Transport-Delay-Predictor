from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class AlertSubscription(Base):
    __tablename__ = "alert_subscriptions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, index=True) # For MVP, simple string (or "demo-user")
    stop_id = Column(String, ForeignKey("stops.stop_id"), nullable=False)
    route_id = Column(String, ForeignKey("routes.route_id"), nullable=True) # Optional filter
    
    threshold_minutes = Column(Float, default=5.0) # Alert if delay > X mins
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_triggered_at = Column(DateTime, nullable=True) # For cooldowns

    stop = relationship("Stop")
    route = relationship("Route")

class NotificationEvent(Base):
    __tablename__ = "notification_events"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    subscription_id = Column(String, ForeignKey("alert_subscriptions.id"))
    message = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_read = Column(Boolean, default=False)
    
    subscription = relationship("AlertSubscription")
