import logging
import mimetypes

import boto3
from botocore.exceptions import ClientError

from app.config import setting

logger = logging.getLogger(__name__)


def get_r2_client():
    # what goes here?
    return boto3.client(
        service_name= "s3",
        endpoint_url= setting.ENDPOINT_URL,
        aws_access_key_id=setting.R2_ACCESS_KEY_ID,
        aws_secret_access_key=setting.R2_SECRET_ACCESS_KEY,
        region_name="auto"
    )

bucket="jobpilot"




def upload_resume(file_bytes: bytes, filename: str, user_id: int) -> str:
    s3 = get_r2_client()
    object_key = f"resumes/{user_id}/{filename}"
    
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = "application/octet-stream"

    try:
        s3.put_object(
            Bucket=setting.R2_BUCKET_NAME,
            Key=object_key,
            Body=file_bytes,
            ContentType=content_type  # Critical for opening PDFs directly in browsers
        )
        logger.info(f"Successfully uploaded resume for user {user_id}: {object_key}")
        return object_key
    except ClientError:
        logger.exception(f"R2 Upload Failed for user {user_id}")
        raise 





def get_resume_url(object_key: str, user_id: int) -> str:
    # generate_presigned_url, return temporary URL
    s3 = get_r2_client()

    try:
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': setting.R2_BUCKET_NAME, 'Key': object_key},
            ExpiresIn=900
        )
        logger.info(f"Successfully generated url for user {user_id}: {object_key}")
        return url


    except ClientError:
        logger.exception(f"Error generating presigned URL for user {user_id}")
        raise 