from datetime import datetime
import uuid

from app.api.admin.model.token import Message
from app.api.dashboard.crud.crud_receipt import receipt_dao
from app.api.dashboard.model.receipt import (
    Receipt,
    ReceiptDetail,
    ReceiptCreate,
    ReceiptFileCreate,
    ReceiptItem,
    ReceiptUpdate,
    ReceiptDelete,
)
from app.api.deps import SessionDep, CurrentUser
from app.core.cloudfront import cloudfront_client
from app.core.openai import openai_client
from fastapi import HTTPException
from sqlmodel.sql.expression import Select


class ReceiptService:
    def get_receipts_list(
        self,
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

    def get_receipt(self, session: SessionDep, id: uuid.UUID) -> ReceiptDetail:
        receipt = receipt_dao.get_receipt_by_id(session=session, id=id)
        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")
        receipt_detail = ReceiptDetail.model_validate(receipt)
        receipt_detail.file_url = cloudfront_client.generate_url(
            receipt_detail.file_name
        )
        return receipt_detail

    def create_receipt(
        self, session: SessionDep, current_user: CurrentUser, receipt_in: ReceiptCreate
    ) -> ReceiptDetail:
        receipt = receipt_dao.create(
            session=session, receipt_in=receipt_in, owner_id=current_user.id
        )
        receipt_detail = ReceiptDetail.model_validate(receipt)
        return receipt_detail

    def update_receipt(
        self,
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

    def delete_receipts(
        self,
        session: SessionDep,
        current_user: CurrentUser,
        receipts_to_delete: ReceiptDelete,
    ) -> None:
        result = receipt_dao.delete_receipts(
            session=session, ids=receipts_to_delete.ids
        )
        if not result:
            raise HTTPException(status_code=404, detail="Receipts not found")

    def create_receipts_by_upload(
        self,
        session: SessionDep,
        current_user: CurrentUser,
        receipts: ReceiptFileCreate,
    ) -> None:
        new_receipts = []

        for receipt in receipts.files:
            image_url = cloudfront_client.generate_url(receipt.file_name)
            response = openai_client.gpt_4o_analyse_image_with_completion(image_url)

            if not response:
                raise HTTPException(
                    status_code=400, detail="Error processing image analysis"
                )

            # One file may contain several receipts
            for extracted_receipt in response:
                new_receipt_items = []

                # Extract receipt items, use hardcoded index to extract items
                for item in extracted_receipt[8]:
                    receiptItem = ReceiptItem(
                        item=item[1],
                        quantity=item[2],
                        unit=item[3],
                        unit_price=item[4],
                        discount_price=item[5],
                        notes=item[6],
                    )
                    new_receipt_items.append(receiptItem)

                # Extract receipt
                new_receipt = ReceiptCreate(
                    description=extracted_receipt[1],
                    date=extracted_receipt[2],
                    category=extracted_receipt[3],
                    amount=extracted_receipt[4],
                    notes=extracted_receipt[5],
                    file_name=receipt.file_name,
                    items=new_receipt_items,
                )

                new_receipts.append(new_receipt)

        receipt_dao.create_receipts(
            session=session, receipts=new_receipts, owner_id=current_user.id
        )


receipt_service = ReceiptService()
