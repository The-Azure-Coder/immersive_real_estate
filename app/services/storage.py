import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings

# Conditionally import boto3 only if S3 is used
if settings.USE_S3:
    import boto3
    from botocore.exceptions import ClientError

    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

async def upload_file(file: UploadFile, folder: str = "") -> str:
    """
    Upload a file to either S3 or local storage based on USE_S3 setting.
    Returns the public URL or local path URL.
    """
    if settings.USE_S3:
        return await _upload_to_s3(file, folder)
    else:
        return await _upload_to_local(file, folder)

async def _upload_to_s3(file: UploadFile, folder: str) -> str:
    """Upload to S3 and return public URL."""
    file_extension = file.filename.split('.')[-1]
    file_key = f"{folder}/{uuid.uuid4()}.{file_extension}"
    try:
        # Reset file pointer to beginning
        await file.seek(0)
        s3_client.upload_fileobj(
            file.file,
            settings.AWS_BUCKET_NAME,
            file_key,
            ExtraArgs={"ACL": "public-read"}
        )
        url = f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
        return url
    except Exception as e:
        raise Exception(f"S3 upload failed: {e}")

async def _upload_to_local(file: UploadFile, folder: str) -> str:
    """Save file locally and return URL path."""
    upload_dir = Path(settings.LOCAL_STORAGE_PATH) / folder
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_extension = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = upload_dir / filename

    await file.seek(0)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/uploads/{folder}/{filename}"
