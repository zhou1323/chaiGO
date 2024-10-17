import uuid
from anyio import sleep
from app.core.celery import celery_app


@celery_app.task()
def test_celery(word: str) -> str:
    return f"test_celery task return {word}"
