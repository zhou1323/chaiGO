from app.api.dashboard.model.receipt import Receipt, ReceiptCreate
from app.api.dashboard.service.receipt_service import receipt_service
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string
from sqlmodel import Session


def create_random_item(db: Session) -> Receipt:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    item_in = ReceiptCreate(title=title, description=description)
    return receipt_service.create_receipt(
        session=db, item_in=item_in, owner_id=owner_id
    )
