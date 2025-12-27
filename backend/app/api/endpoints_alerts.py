from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.alerts import AlertSubscription, NotificationEvent
from app.schemas.alerts import AlertSubscriptionCreate, AlertSubscriptionResponse, NotificationResponse
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/alerts", response_model=AlertSubscriptionResponse)
def create_subscription(
    subscription: AlertSubscriptionCreate, 
    db: Session = Depends(get_db)
):
    """Create a new delay alert subscription."""
    db_obj = AlertSubscription(
        stop_id=subscription.stop_id,
        route_id=subscription.route_id,
        threshold_minutes=subscription.threshold_minutes,
        user_id=subscription.user_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/alerts", response_model=List[AlertSubscriptionResponse])
def list_subscriptions(user_id: str = "demo-user", db: Session = Depends(get_db)):
    """List active subscriptions for a user."""
    return db.query(AlertSubscription).filter(
        AlertSubscription.user_id == user_id,
        AlertSubscription.is_active == True
    ).all()

@router.get("/notifications", response_model=List[NotificationResponse])
def list_notifications(user_id: str = "demo-user", db: Session = Depends(get_db)):
    """Get recent notifications (from triggered alerts)."""
    # Join subscription to filter by user
    return db.query(NotificationEvent).join(AlertSubscription).filter(
        AlertSubscription.user_id == user_id
    ).order_by(NotificationEvent.created_at.desc()).limit(20).all()
