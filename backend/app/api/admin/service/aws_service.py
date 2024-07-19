from fastapi import HTTPException
from app.core.aws_s3 import s3_client
from app.core.cloudfront import cloudfront_client


class AwsService:
    @staticmethod
    def generate_presigned_url(*, file_name: str):
        url = s3_client.generate_presigned_url(file_name=file_name)
        if not url:
            raise HTTPException(status_code=425, detail="Error generating URL")
        return url

    @staticmethod
    def generate_presigned_cookie():
        cookie = cloudfront_client.generate_cookie()
        if not cookie:
            raise HTTPException(status_code=425, detail="Error generating cookie")
        return cookie


aws_service = AwsService()
