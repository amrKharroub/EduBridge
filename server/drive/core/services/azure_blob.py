from datetime import datetime, timedelta
from azure.storage.blob import (
    BlobServiceClient,
    generate_blob_sas,
    BlobSasPermissions,
    BlobBlock,
)
import io
import uuid
from django.conf import settings
from azure.identity import DefaultAzureCredential
from urllib.parse import quote

def get_blob_service():
    if settings.USE_AZURE_IDENTITY:
        print("we should not be here: ", settings.USE_AZURE_IDENTITY)
        exit()
        return BlobServiceClient(
            account_url=settings.AZURE_STORAGE_BLOB_ENDPOINT,
            credential=DefaultAzureCredential()
        )
    else:
        return BlobServiceClient.from_connection_string(
            settings.AZURE_CONNECTION_STRING
        )

def generate_upload_sas(blob_ref:str, container_name:str = "files"):
    permissions = BlobSasPermissions(write=True, create=True)
    return generate_sas(blob_ref, permissions, container_name)

def generate_download_sas(blob_ref:str, container_name:str = "files"):
    permissions = BlobSasPermissions(read=True)
    return generate_sas(blob_ref, permissions, container_name)

def generate_sas(blob_ref: str, permissions: BlobSasPermissions, content_disposition:str, container_name:str = "files"):
    client = get_blob_service()
    start = datetime.now()
    expiry = start + timedelta(hours=1)

    if settings.USE_AZURE_IDENTITY:
        exit()
        user_delegation_key = client.get_user_delegation_key(
            key_start_time=start,
            key_expiry_time=expiry
        )
        sas_token = generate_blob_sas(
            account_name=settings.AZURE_STORAGE_ACCOUNT_NAME,
            container_name=container_name,
            blob_name=blob_ref,
            user_delegation_key=user_delegation_key,
            permission=permissions,
            expiry=expiry
        )
    else:
        sas_token = generate_blob_sas(
            account_name=client.account_name,
            container_name=container_name,
            blob_name=blob_ref,
            account_key=client.credential.account_key,
            permission=permissions,
            expiry=expiry
        )
    safe_blob_ref = quote(blob_ref)
    return f"{client.url}{container_name}/{safe_blob_ref}?{sas_token}"

    
def get_file_metadata(storage_key:str, container_name:str = 'files'):
    blob_client = get_blob_service().get_blob_client(container=container_name, blob=storage_key)
    if not blob_client.exists():
        return {"status": False, "message": "file not found"}
    props = blob_client.get_blob_properties()
    return {
        "status": True,
        "size": props.size,
        "type": props.content_settings.content_type,
        "content_md5": props.content_settings.content_md5,
        "last_modified": props.last_modified
    }

class AzureBlockStreamer(io.RawIOBase):
    def __init__(self, blob_client, chunk_size=4 * 1024 * 1024):
        self.blob_client = blob_client
        self.chunk_size = chunk_size
        self.buffer = io.BytesIO()
        self.block_ids = []
        self._absolute_position = 0

    def write(self, b):
        self.buffer.write(b)
        self._absolute_position += len(b)
        
        if self.buffer.tell() >= self.chunk_size:
            self.flush_to_azure()
        return len(b)

    def tell(self):
        return self._absolute_position

    def flush_to_azure(self):
        self.buffer.seek(0)
        data = self.buffer.read()
        if not data:
            return

        block_id = uuid.uuid4().hex

        self.blob_client.stage_block(block_id=block_id, data=data)
        self.block_ids.append(BlobBlock(block_id=block_id))

        self.buffer = io.BytesIO()

    def finalize(self):
        self.flush_to_azure()
        self.blob_client.commit_block_list(self.block_ids)

    def seekable(self):
        return False 
