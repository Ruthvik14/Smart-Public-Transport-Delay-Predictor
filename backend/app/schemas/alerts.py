from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertSubscriptionCreate(BaseModel):
    stop_id: str
    route_id: Optional[str] = None
    threshold_minutes: float = 5.0
    user_id: str = "demo-user"

class AlertSubscriptionResponse(AlertSubscriptionCreate):
    id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: str
    message: str
    created_at: datetime
    is_read: bool
    
    class Config:
        from_attributes = True
