from datetime import datetime, timedelta
from botocore.signers import CloudFrontSigner
from app.core.config import settings
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding


def rsa_signer(message):
    private_key = serialization.load_pem_private_key(
        # load the private key from the environment variable as a string
        settings.CLOUDFRONT_PRIVATE_KEY_STRING.encode(),
        password=None,
        backend=default_backend(),
    )
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())


class CloudFrontClient:
    def __init__(self):
        self.signer = CloudFrontSigner(settings.CLOUDFRONT_KEY_ID, rsa_signer)

    # These cookies and urls are used to get files in S3 bucket through cloudfront
    def generate_cookie(self):
        key_id = settings.CLOUDFRONT_KEY_ID
        # Must be a wildcard!
        url = settings.CLOUDFRONT_DISTRIBUTION_DOMAIN + "/*"

        expire_at = datetime.now() + timedelta(hours=1)

        policy = self.signer.build_policy(url, date_less_than=expire_at).encode("utf8")
        policy_64 = self.signer._url_b64encode(policy).decode("utf8")

        signature = rsa_signer(policy)
        signature_64 = self.signer._url_b64encode(signature).decode("utf8")

        return {
            "CloudFront-Domain": settings.CLOUDFRONT_DISTRIBUTION_DOMAIN,
            "CloudFront-Policy": policy_64,
            "CloudFront-Signature": signature_64,
            "CloudFront-Key-Pair-Id": key_id,
        }

    def generate_url(self, file_name: str):
        url = settings.CLOUDFRONT_DISTRIBUTION_DOMAIN + "/" + file_name

        expire_at = datetime.now() + timedelta(hours=1)

        signed_url = self.signer.generate_presigned_url(url, date_less_than=expire_at)

        return signed_url


cloudfront_client = CloudFrontClient()
