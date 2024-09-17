import uuid
from anyio import sleep
from app.core.celery import celery_app


@celery_app.task(name="test_celery")
async def test_celery() -> str:
    await sleep(1)
    uid = uuid.uuid4().hex
    print(f"Task {uid} executed successfully")
    return uid
