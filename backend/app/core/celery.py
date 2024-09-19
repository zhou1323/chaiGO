from celery import Celery
from app.core.config import settings
from urllib.parse import quote_plus

redis_broker = (
    f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:"
    f"{settings.REDIS_PORT}"
)


redis_backend = (
    f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:"
    f"{settings.REDIS_PORT}"
)

postgres_backend = (
    f"db+postgresql://{settings.POSTGRES_USER}:"
    f"{quote_plus(settings.POSTGRES_PASSWORD)}@{settings.POSTGRES_SERVER}:"
    f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)


celery_app = Celery("worker", broker=redis_broker, backend=postgres_backend)

celery_app.conf.broker_connection_retry_on_startup = True

# Run tasks synchronously for testing
# celery_app.conf.task_always_eager = True

# Assign tasks to the main queue, which is used by the worker command
celery_app.conf.task_routes = {
    "app.api.task.celery_task.tasks.*": "main-queue",
    "app.api.task.celery_task.receipt.tasks.*": "main-queue",
}

# Autodiscover tasks in the specified module
# Tasks must be in the files named tasks.py!
celery_app.autodiscover_tasks(
    ["app.api.task.celery_task", "app.api.task.celery_task.receipt"]
)
