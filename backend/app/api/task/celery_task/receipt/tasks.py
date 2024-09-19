import uuid
from app.core.celery import celery_app
from app.api.dashboard.model.receipt import Receipt
from app.api.admin.model.user import User
from app.api.deps import get_db


@celery_app.task()
def process_receipts_upload_task(user_id_str: str, receipts_data: list[str]):
    user_id = uuid.UUID(user_id_str)
    db = next(get_db())
    current_user = db.get(User, user_id)
    receipts = [Receipt.model_validate_json(receipt) for receipt in receipts_data]

    try:
        from app.api.dashboard.service.receipt_service import receipt_service

        receipt_service.process_receipts_upload(db, current_user, receipts)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
