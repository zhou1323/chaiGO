from typing import Annotated
from app.api.admin.service.aws_service import aws_service
from app.api.deps import get_current_user
from app.common.response.response_schema import response_base
from fastapi import APIRouter, Depends, Query, Response

router = APIRouter(dependencies=[Depends(get_current_user)])


# To put images in S3 bucket
@router.get("/generate-presigned-url")
async def generate_presigned_url(
    file_name: Annotated[str | None, Query(alias="fileName")] = None,
):
    url = aws_service.generate_presigned_url(file_name=file_name)
    return await response_base.success(data={"url": url})


@router.get("/generate-presigned-cookie")
async def generate_presigned_cookie(response: Response):
    cookie = aws_service.generate_presigned_cookie()

    for key, value in cookie.items():
        response.set_cookie(
            key=key,
            value=value,
            secure=True,
            httponly=True,
        )

    return await response_base.success()
