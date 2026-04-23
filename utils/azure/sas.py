from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from django.conf import settings


def generate_sas_url(blob_name: str) -> str:
    sas_token = generate_blob_sas(
        account_name=settings.AZURE_ACCOUNT_NAME,
        container_name=settings.AZURE_CONTAINER_MEDIA,
        blob_name=blob_name,
        account_key=settings.AZURE_ACCOUNT_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(
            minutes=settings.AZURE_BLOB_SAS_TOKEN_LIFETIME_MINUTES
        ),
    )

    return (
        f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/"
        f"{settings.AZURE_CONTAINER_MEDIA}/{blob_name}?{sas_token}"
    )