from datetime import datetime, timedelta
import uuid

from app.api.admin.model.token import Message
from app.api.admin.model.user import User
from app.api.dashboard.crud.crud_receipt import receipt_dao
from app.api.dashboard.model.receipt import (
    Receipt,
    ReceiptDetail,
    ReceiptCreate,
    ReceiptFileCreate,
    ReceiptItem,
    ReceiptPublic,
    ReceiptUpdate,
    ReceiptDelete,
)
from app.api.dashboard.service.budget_service import budget_service
from app.api.deps import SessionDep, CurrentUser
from app.api.task.celery_task.receipt.tasks import process_receipts_upload_task
from app.api.task.service.task_service import task_service
from app.core.cloudfront import cloudfront_client
from app.core.openai import openai_client
from fastapi import HTTPException
from sqlmodel import Session
from sqlmodel.sql.expression import Select


class ReceiptService:
    def get_receipt_list_statement(
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

        if receipt_detail.file_name:
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
        self.update_budget(
            session=session,
            current_user=current_user,
            dates=[receipt.date],
        )
        receipt_detail = ReceiptDetail.model_validate(receipt)
        return receipt_detail

    def update_receipt(
        self,
        session: SessionDep,
        id: uuid.UUID,
        current_user: CurrentUser,
        receipt_in: ReceiptUpdate,
    ) -> ReceiptDetail:
        receipt = receipt_dao.get_receipt_by_id(session=session, id=id)
        if not receipt:
            raise HTTPException(status_code=404, detail="Item not found")
        update_receipt = receipt_dao.update_receipt(
            session=session, current_receipt=receipt, receipt_in=receipt_in
        )
        self.update_budget(
            session=session,
            current_user=current_user,
            dates=[
                receipt.date,
                update_receipt.date,
            ],  # the previous ones also should be updated
        )
        receipt_detail = ReceiptDetail.model_validate(update_receipt)
        return receipt_detail

    def delete_receipts(
        self,
        session: SessionDep,
        current_user: CurrentUser,
        receipts_to_delete: ReceiptDelete,
    ) -> None:
        receipts = receipt_dao.get_receipts_by_ids(
            session=session, ids=receipts_to_delete.ids
        )
        receipt_dao.delete_receipts(session=session, receipts=receipts)

        if not receipts or len(receipts) != len(receipts_to_delete.ids):
            raise HTTPException(status_code=404, detail="Receipts not found")

        self.update_budget(
            session=session,
            current_user=current_user,
            dates=[receipt.date for receipt in receipts],
        )

    def create_receipts_by_upload(
        self,
        session: SessionDep,
        current_user: CurrentUser,
        receipt_files: ReceiptFileCreate,
    ) -> None:
        # Create placeholder receipts
        placeholder_receipts = []
        for receipt_file in receipt_files.files:
            placeholder_receipt = ReceiptCreate(
                category="groceries",
                description=receipt_file.file_name,
                file_name=receipt_file.file_name,
            )
            placeholder_receipts.append(placeholder_receipt)

        receipts_db = receipt_dao.create_receipts(
            session=session, receipts=placeholder_receipts, owner_id=current_user.id
        )

        # Start Celery task
        task = process_receipts_upload_task.delay(
            str(current_user.id),
            [receipt.model_dump_json() for receipt in receipts_db],
        )

        receipt_dao.update_receipt_tasks_status(
            session=session, receipts=receipts_db, task_id=task.id
        )

    def process_receipts_upload(
        self,
        session: Session,
        current_user: User,
        receipts: list[Receipt],
    ):
        to_update_receipts = []
        to_create_receipts = []

        for receipt_file in receipts:
            image_url = cloudfront_client.generate_url(receipt_file.file_name)
            response = openai_client.gpt_4o_analyse_image_with_completion(image_url)

            if not response:
                raise HTTPException(
                    status_code=400, detail="Error processing image analysis"
                )

            # One file may contain several receipts
            receipt_num = 1
            for extracted_receipt in response["receipts"]:
                receipt_items = []

                # Extract receipt items, use hardcoded index to extract items
                for item in extracted_receipt["details"]:
                    # Create receipt item with information in item
                    receiptItem = ReceiptItem(
                        item=item["item"],
                        quantity=item["quantity"],
                        unit=item["unit"],
                        unit_price=item["unitPrice"],
                        discount_price=item["discountPrice"],
                        notes=item["notes"],
                    )
                    receipt_items.append(receiptItem)

                # Extract receipt
                if receipt_num == 1:
                    new_receipt = ReceiptUpdate(
                        id=receipt_file.id,
                        description=extracted_receipt["description"],
                        date=extracted_receipt["date"],
                        category=extracted_receipt["category"],
                        amount=extracted_receipt["amount"],
                        notes=extracted_receipt["notes"],
                        file_name=receipt_file.file_name,
                        items=receipt_items,
                    )
                    to_update_receipts.append(new_receipt)
                else:
                    new_receipt = ReceiptCreate(
                        description=extracted_receipt["description"],
                        date=extracted_receipt["date"],
                        category=extracted_receipt["category"],
                        amount=extracted_receipt["amount"],
                        notes=extracted_receipt["notes"],
                        file_name=receipt_file.file_name,
                        items=receipt_items,
                    )
                    to_create_receipts.append(new_receipt)

                receipt_num += 1

        # Create receipts
        receipt_dao.create_receipts(
            session=session, receipts=to_create_receipts, owner_id=current_user.id
        )

        # Update receipts
        for receipt_to_update in to_update_receipts:
            current_receipt = receipt_dao.get_receipt_by_id(
                session=session, id=receipt_to_update.id
            )
            if not current_receipt:
                raise HTTPException(status_code=404, detail="Item not found")

            receipt_dao.update_receipt(
                session=session,
                current_receipt=current_receipt,
                receipt_in=receipt_to_update,
            )

        self.update_budget(
            session=session,
            current_user=current_user,
            dates=(
                receipt.date for receipt in (to_create_receipts + to_update_receipts)
            ),
        )

    def update_receipt_task_status(self, receipt: ReceiptPublic):
        if receipt.task_id:
            task_result = task_service.get_result(receipt.task_id)
            receipt.task_status = task_result.status
            if task_result.successful():
                receipt.task_message = task_result.info
            else:
                receipt.task_message = task_result.traceback
        return receipt

    # Update budget when update receipts
    def update_budget(
        self, session: SessionDep, current_user: CurrentUser, dates: list[datetime]
    ) -> None:
        str_dates = set([date.strftime("%Y-%m") for date in dates])

        for str_date in str_dates:
            self.update_budget_recorded_expense(
                session=session,
                current_user=current_user,
                date=datetime.strptime(str_date, "%Y-%m"),
            )

    def update_budget_recorded_expense(
        self, session: SessionDep, current_user: CurrentUser, date: datetime
    ):
        start_date = datetime(date.year, date.month, 1)
        end_date = datetime(date.year, date.month + 1, 1) - timedelta(days=1)

        receipts = receipt_dao.get_receipt_list(
            session=session,
            owner_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
        )

        total_amount = sum(receipt.amount for receipt in receipts)

        month_str = date.strftime("%Y-%m")

        budget_service.create_budget_from_receipts(
            session=session,
            current_user=current_user,
            date=month_str,
            amount=total_amount,
        )


receipt_service = ReceiptService()
