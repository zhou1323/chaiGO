from app.api.dashboard.model.receipt import ReceiptFileCreate
from app.api.dashboard.service.receipt_service import receipt_service
from app.api.deps import CurrentUser, SessionDep
from app.common.response.response_schema import response_base
from fastapi import APIRouter

router = APIRouter()


@router.post("/create-receipts-by-upload")
async def create_receipts_by_upload(
    session: SessionDep, current_user: CurrentUser, receipts: ReceiptFileCreate
):
    receipt_service.create_receipts_by_upload(
        session=session, current_user=current_user, receipt_files=receipts
    )
    return await response_base.success()
