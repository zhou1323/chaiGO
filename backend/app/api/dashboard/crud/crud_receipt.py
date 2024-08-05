from datetime import datetime
from typing import List
import uuid

from app.api.dashboard.model.receipt import (
    ReceiptCreate,
    Receipt,
    ReceiptFileCreate,
    ReceiptUpdate,
    ReceiptItem,
)
from sqlmodel import Session, select, delete
from sqlmodel.sql.expression import Select


class ReceiptDAO:
    def create(
        self, session: Session, receipt_in: ReceiptCreate, owner_id: uuid.UUID
    ) -> Receipt:
        db_item = Receipt.model_validate(receipt_in, update={"owner_id": owner_id})
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item

    def create_receipts(
        self, session: Session, receipts: List[ReceiptCreate], owner_id: uuid.UUID
    ) -> None:
        # Can generate id for each receipt automatically
        for receipt in receipts:
            db_item = Receipt.model_validate(receipt, update={"owner_id": owner_id})
            session.add(db_item)
        session.commit()

    def get_receipt_list(
        self,
        session: Session,
        owner_id: uuid.UUID,
        description: str | None = None,
        category: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        order_by: str | None = None,
        order_type: str | None = None,
    ) -> List[Receipt]:
        statement = self.get_receipt_list_statement(
            owner_id=owner_id,
            description=description,
            category=category,
            start_date=start_date,
            end_date=end_date,
            order_by=order_by,
            order_type=order_type,
        )
        receipts = session.exec(statement).all()
        return receipts

    def get_receipt_list_statement(
        self,
        owner_id: uuid.UUID,
        description: str | None = None,
        category: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        order_by: str | None = None,
        order_type: str | None = None,
    ) -> Select:
        statement = select(Receipt).where(Receipt.owner_id == owner_id)

        if description and description != "":
            statement = statement.where(
                Receipt.description.like("%" + description + "%")
            )

        if category and category != "":
            statement = statement.where(Receipt.category == category)

        if start_date and start_date != "":
            statement = statement.where(Receipt.date >= start_date)

        if end_date and end_date != "":
            statement = statement.where(Receipt.date <= end_date)

        if order_by and order_by != "":
            order_column = getattr(Receipt, order_by)
            statement = statement.order_by(
                order_column.desc() if order_type == "desc" else order_column
            )
        else:
            statement = statement.order_by(Receipt.date.desc())

        return statement

    def get_receipt_by_id(self, session: Session, id: uuid.UUID) -> Receipt:
        receipt = session.get(Receipt, id)
        return receipt

    def get_receipts_by_ids(
        self, session: Session, ids: List[uuid.UUID]
    ) -> List[Receipt]:
        receipts = session.exec(select(Receipt).where(Receipt.id.in_(ids))).all()
        return receipts

    def update_receipt(
        self, session: Session, current_receipt: Receipt, receipt_in: ReceiptUpdate
    ) -> Receipt:
        update_dict = receipt_in.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            if key != "items":
                setattr(current_receipt, key, value)
            else:
                items = update_dict["items"]
                # Delete current receipt items
                session.exec(
                    delete(ReceiptItem).where(
                        ReceiptItem.receipt_id == current_receipt.id
                    )
                )
                # Add new receipt items
                for item in items:
                    item_db = ReceiptItem.model_validate(
                        item, update={"receipt_id": current_receipt.id}
                    )
                    session.add(item_db)

        session.add(current_receipt)
        session.commit()
        session.refresh(current_receipt)
        return current_receipt

    def delete_receipts(self, session: Session, receipts: List[Receipt]) -> None:
        for receipt in receipts:
            session.delete(receipt)

        session.commit()

    def create_receipts_by_upload(
        self, session: Session, receipts: ReceiptFileCreate, owner_id: uuid.UUID
    ) -> None:
        for receipt in receipts.files:
            db_item = Receipt.model_validate(
                receipt,
                update={
                    "owner_id": owner_id,
                    "category": "groceries",
                    "description": receipt.file_name,
                },
            )
            session.add(db_item)
        session.commit()


receipt_dao = ReceiptDAO()
