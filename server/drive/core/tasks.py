import zipfile
from celery import shared_task
from drive.core.services.azure_blob import generate_download_sas
from drive.core.services.azure_blob import get_blob_service, AzureBlockStreamer
from drive.models import ZipFolder
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def stream_upload(streamer, container, files):
    with zipfile.ZipFile(streamer, mode='w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        for blob_name, arcname in files:
            src_blob = container.get_blob_client(blob_name)
            
            with zf.open(arcname, "w") as zf_entry:
                download_stream = src_blob.download_blob()
                for chunk in download_stream.chunks():
                    zf_entry.write(chunk)

    streamer.finalize()

@shared_task(bind=True)
def generate_and_upload_zip_task(
    self,
    zipfolder_id: int,
    zipfile_storage_key: str,
    zip_filename: str,
    files_info: list[tuple[str, str]],
    zip_container_name: str = "zips",
    files_container_name: str = "files"
):
    blob_service_client = get_blob_service()
    blob_client = blob_service_client.get_blob_client(container=zip_container_name, blob=zipfile_storage_key)
    streamer = AzureBlockStreamer(blob_client)
    container = blob_service_client.get_container_client(files_container_name)
    try:
        stream_upload(streamer=streamer, container=container, files=files_info)
        download_sas_url = generate_download_sas(zipfile_storage_key, zip_container_name)
        ZipFolder.objects.filter(pk=zipfolder_id).update(
            status=ZipFolder.ZipFolderStatus.COMPLETED
        )

        return {
            "status": "success",
            "filename": zip_filename,
            "download_url": download_sas_url
        }

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        if self.request.retries >= self.max_retries:
            ZipFolder.objects.filter(pk=zipfolder_id).update(
                status=ZipFolder.ZipFolderStatus.FAILED
            )
        raise self.retry(exc=e, countdown=60, max_retries=3)