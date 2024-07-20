from datetime import datetime

from app.api.admin.model.token import Message
from app.api.dashboard.crud.crud_receipt import receipt_dao
from app.api.dashboard.model.receipt import (
    ReceiptDetail,
    ReceiptCreate,
    ReceiptFileCreate,
    ReceiptUpdate,
    ReceiptDelete,
)
from app.api.deps import SessionDep, CurrentUser
from app.core.cloudfront import cloudfront_client
from fastapi import HTTPException
from sqlmodel.sql.expression import Select


class ReceiptService:
    @staticmethod
    def get_receipts_list(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        description: str | None = None,
        category: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        order_by: str | None = None,
        order_type: str | None = None,
    ) -> Select:
        statement = receipt_dao.get_receipt_list_statement(
            owner_id=current_user.id,
            description=description,
            category=category,
            start_date=start_date,
            end_date=end_date,
            order_by=order_by,
            order_type=order_type,
        )
        return statement

    @staticmethod
    def get_receipt(*, session: SessionDep, id: int) -> ReceiptDetail:
        receipt = receipt_dao.get_receipt_by_id(session=session, id=id)
        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")
        receipt_detail = ReceiptDetail.model_validate(receipt)
        receipt_detail.file_url = cloudfront_client.generate_url(
            receipt_detail.file_name
        )
        return receipt_detail

    @staticmethod
    def create_receipt(
        *, session: SessionDep, current_user: CurrentUser, receipt_in: ReceiptCreate
    ) -> ReceiptDetail:
        receipt = receipt_dao.create(
            session=session, receipt_in=receipt_in, owner_id=current_user.id
        )
        receipt_detail = ReceiptDetail.model_validate(receipt)
        return receipt_detail

    @staticmethod
    def update_receipt(
        *,
        session: SessionDep,
        id: str,
        current_user: CurrentUser,
        receipt_in: ReceiptUpdate,
    ) -> ReceiptDetail:
        receipt = receipt_dao.get_receipt_by_id(session=session, id=id)
        if not receipt:
            raise HTTPException(status_code=404, detail="Item not found")
        update_receipt = receipt_dao.update_receipt(
            session=session, current_receipt=receipt, receipt_in=receipt_in
        )
        receipt_detail = ReceiptDetail.model_validate(update_receipt)
        return receipt_detail

    @staticmethod
    def delete_receipts(
        *,
        session: SessionDep,
        current_user: CurrentUser,
        receipts_to_delete: ReceiptDelete,
    ) -> None:
        receipt_dao.delete_receipts(session=session, ids=receipts_to_delete.ids)

    @staticmethod
    def create_receipts_by_upload(
        *, session: SessionDep, current_user: CurrentUser, receipts: ReceiptFileCreate
    ) -> None:
        receipt_dao.create_receipts_by_upload(
            session=session, receipts=receipts, owner_id=current_user.id
        )


receipt_service = ReceiptService()
