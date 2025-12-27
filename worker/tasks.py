from celery import Celery
import os

from app.core.config import settings

# Ensure REDIS_URL is set
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery("tasks", broker=redis_url, backend=redis_url)

# Load tasks
import ingest
import alerts

app.conf.timezone = 'UTC'
