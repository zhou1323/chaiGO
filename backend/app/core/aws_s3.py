import boto3
from app.core.config import settings


class S3Client:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME,
        )

    def generate_presigned_url(self, file_name: str, expiration=3600):
        try:
            response_url = self.client.generate_presigned_url(
                "put_object",
                Params={"Bucket": settings.AWS_BUCKET_NAME, "Key": file_name},
                ExpiresIn=expiration,
            )
        except Exception as e:
            print(e)
            return None
        return response_url

    def delete_file(self, file_name: str):
        try:
            self.client.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=file_name)
        except Exception as e:
            print(e)
            return False
        return True


s3_client = S3Client()
