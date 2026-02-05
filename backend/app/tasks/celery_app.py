"""
Celery Configuration and Tasks
"""
from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "heyai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.generation_tasks", "app.tasks.video_tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_max_tasks_per_child=50,
)

if __name__ == "__main__":
    celery_app.start()
