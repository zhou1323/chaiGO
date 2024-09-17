from celery import Celery
from app.core.config import settings

redis_broker = (
    f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:"
    f"{settings.REDIS_PORT}"
)


redis_backend = (
    f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:"
    f"{settings.REDIS_PORT}"
)

celery_app = Celery(
    "worker",
    broker=redis_broker,
    backend=redis_backend,
)

celery_app.conf.task_routes = {
    "app.api.task.celery_task.tasks.test_celery": "main-queue"
}
