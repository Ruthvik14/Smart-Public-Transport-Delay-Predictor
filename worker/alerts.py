from tasks import app
from app.db.session import SessionLocal
from app.models.alerts import AlertSubscription, NotificationEvent
from app.services.gtfs_rt import parse_trip_updates, fetch_feed, TRIP_UPDATES_URL
import datetime

@app.on_after_configure.connect
def setup_alert_tasks(sender, **kwargs):
    # Check Alerts every 60 seconds
    sender.add_periodic_task(60.0, check_alerts.s(), name='check-alerts-60s')

@app.task
def check_alerts():
    """
    Evaluates active subscriptions against current real-time delays.
    Simple MVP Implementation:
    1. Fetch all active subscriptions.
    2. Fetch latest GTFS-RT Trip Updates.
    3. Match stop_id/route_id.
    4. If delay > threshold, create NotificationEvent.
    """
    db = SessionLocal()
    try:
        subscriptions = db.query(AlertSubscription).filter(AlertSubscription.is_active == True).all()
        if not subscriptions:
            return "No active subscriptions"

        # Fetch live data (In production, maybe read from Redis cache to avoid re-fetch)
        feed = fetch_feed(TRIP_UPDATES_URL)
        updates = parse_trip_updates(feed)
        
        # Index updates by route and vehicle for faster lookup (O(N) -> O(1))
        # Map: (route_id, stop_id) -> delay_seconds
        delays_map = {} 
        
        for u in updates:
            route_id = u['route_id']
            for stu in u['stop_time_updates']:
                stop_id = stu['stop_id']
                delay = stu.get('arrival_delay', 0)
                delays_map[(route_id, stop_id)] = delay

        triggered_count = 0
        
        for sub in subscriptions:
            # Check if cooldown passed (e.g., 15 mins)
            if sub.last_triggered_at:
                diff = datetime.datetime.now() - sub.last_triggered_at
                if diff.total_seconds() < 900: # 15 mins
                    continue

            # Look for delay
            # Note: GTFS-RT 'stop_id' might differ slightly from static ID? (Sometimes implicit)
            # We assume they match here.
            
            # Since subscription might not specify route, we check all routes if route_id is None?
            # Or simplified: User subscribes to Stop X. We check any Trip at Stop X.
            
            current_delay = 0
            
            # This lookup is imperfect because different routes stop at the same stop using same StopID? 
            # Yes. So we need to find MAX delay at this stop for the relevant route?
            
            found = False
            for (r_id, s_id), d_sec in delays_map.items():
                if sub.route_id and sub.route_id != r_id:
                    continue # Filter by route if specified
                
                if s_id == sub.stop_id:
                    delay_min = d_sec / 60.0
                    if delay_min >= sub.threshold_minutes:
                        # TRIGGER
                        msg = f"Delay Alert: Route {r_id} at Stop {s_id} is {int(delay_min)} mins late."
                        
                        notification = NotificationEvent(
                            subscription_id=sub.id,
                            message=msg
                        )
                        db.add(notification)
                        sub.last_triggered_at = datetime.datetime.now()
                        found = True
                        triggered_count += 1
                        break # One notification per sweep per sub
            
        db.commit()
        return f"Checked alerts. Triggered {triggered_count} notifications."

    except Exception as e:
        db.rollback()
        print(f"Error checking alerts: {e}")
    finally:
        db.close()
