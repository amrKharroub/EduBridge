from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from allauth.headless.contrib.rest_framework.authentication import XSessionTokenAuthentication
from drive.models import Node
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from embed.models import NodeVectorUsage
from celery import current_app
from drive.core.services.azure_blob import generate_download_sas
from django.conf import settings
from drive.utils.permissions import can_edit
from drive.core.services.redis_cache import redis_client, VECTOR_OWNER_KEY, VECTOR_STATUS_KEY
import uuid

# Complete mapping of extensions to MIME types
MIME_TYPE_MAP = {
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '602': 'application/x-t602',
    'abw': 'application/x-abiword',
    'cgm': 'image/cgm',
    'cwk': 'application/x-appleworks',
    'doc': 'application/msword',
    'docm': 'application/vnd.ms-word.document.macroEnabled.12',
    'dot': 'application/msword',
    'dotm': 'application/vnd.ms-word.template.macroEnabled.12',
    'hwp': 'application/x-hwp',
    'key': 'application/vnd.apple.keynote',
    'lwp': 'application/vnd.lotus-wordpro',
    'mw': 'application/macwriteii',
    'mcw': 'application/x-macwriteii',
    'pages': 'application/vnd.apple.pages',
    'pbd': 'application/vnd.powerbuilder',
    'ppt': 'application/vnd.ms-powerpoint',
    'pptm': 'application/vnd.ms-powerpoint.presentation.macroEnabled.12',
    'pot': 'application/vnd.ms-powerpoint',
    'potm': 'application/vnd.ms-powerpoint.template.macroEnabled.12',
    'potx': 'application/vnd.openxmlformats-officedocument.presentationml.template',
    'rtf': 'text/rtf',
    'sda': 'application/vnd.stardivision.draw',
    'sdd': 'application/vnd.stardivision.impress',
    'sdp': 'application/sdp',
    'sdw': 'application/vnd.stardivision.writer',
    'sgl': 'application/vnd.stardivision.writer-global',
    'sti': 'application/vnd.sun.xml.impress.template',
    'sxi': 'application/vnd.sun.xml.impress',
    'sxw': 'application/vnd.sun.xml.writer',
    'stw': 'application/vnd.sun.xml.writer.template',
    'sxg': 'application/vnd.sun.xml.writer.global',
    'txt': 'text/plain',
    'uof': 'application/vnd.uoml+xml',
    'uop': 'application/vnd.uoml+xml',
    'uot': 'application/vnd.uoml+xml',
    'vor': 'application/vnd.stardivision.writer',
    'wpd': 'application/vnd.wordperfect',
    'wps': 'application/vnd.ms-works',
    'xml': 'application/xml',
    'zabw': 'application/x-abiword',
    'epub': 'application/epub+zip',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'bmp': 'image/bmp',
    'svg': 'image/svg+xml',
    'tiff': 'image/tiff',
    'webp': 'image/webp',
    'htm': 'text/html',
    'html': 'text/html',
    'web': 'application/x-web',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'xls': 'application/vnd.ms-excel',
    'xlsm': 'application/vnd.ms-excel.sheet.macroEnabled.12',
    'xlsb': 'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
    'xlw': 'application/vnd.ms-excel',
    'csv': 'text/csv',
    'dif': 'application/x-dif',
    'sylk': 'application/x-sylk',
    'slk': 'application/x-slk',
    'prn': 'text/plain',  
    'numbers': 'application/vnd.apple.numbers',
    'et': 'application/x-etable',
    'ods': 'application/vnd.oasis.opendocument.spreadsheet',
    'fods': 'application/vnd.oasis.opendocument.spreadsheet.flat',
    'uos1': 'application/vnd.uoml+xml',
    'uos2': 'application/vnd.uoml+xml',
    'dbf': 'application/x-dbase',
    'wk1': 'application/x-lotus',
    'wk2': 'application/x-lotus',
    'wk3': 'application/x-lotus',
    'wk4': 'application/x-lotus',
    'wks': 'application/vnd.ms-works',
    '123': 'application/x-lotus',
    'wq1': 'application/x-quattropro',
    'wq2': 'application/x-quattropro',
    'wb1': 'application/x-quattropro',
    'wb2': 'application/x-quattropro',
    'wb3': 'application/x-quattropro',
    'qpw': 'application/x-quattropro',
    'xlr': 'application/vnd.ms-works',
    'eth': 'application/x-eth', 
    'tsv': 'text/tab-separated-values',
    'mp3': 'audio/mpeg',
    'mp4': 'video/mp4',
    'mpeg': 'video/mpeg',
    'mpga': 'audio/mpeg',
    'm4a': 'audio/mp4',
    'wav': 'audio/wav',
    'webm': 'video/webm'
}
SUPPORTED_MIME_TYPES = set(MIME_TYPE_MAP.values())



# Create your views here.
class VectoriseNode(APIView):
    #authenticated
    authentication_classes = [
        XSessionTokenAuthentication
    ]
    permission_classes = [
        IsAuthenticated
    ]
    def post(self, request, node_id):
        node = get_object_or_404(Node.active_objects.select_related("current_version"), pk=node_id)
        if node.is_folder:
            return Response("Node should be a file", status=status.HTTP_400_BAD_REQUEST)
        if not can_edit(request.user, node):
            return Response("Permission Deneid", status=status.HTTP_403_FORBIDDEN)
        if not node.current_version.mime_type in SUPPORTED_MIME_TYPES:
            return Response("Unsupported document type", status=status.HTTP_400_BAD_REQUEST)
        download_sas_url = generate_download_sas(blob_ref=node.current_version.storage_key)
        parse_settings = settings.PARSE_SETTINGS.copy()
        if "source_url" in parse_settings:
            parse_settings["source_url"] = download_sas_url
        task_id = str(uuid.uuid4())
        data = {
            "llama_cloud_key": settings.LLAMA_CLOUD_KEY,
            "connection_url": settings.QDRANT_CONNECTION,
            "collection_name": settings.QDRANT_COLLECTION_NAME,
            "model_name": settings.QDRANT_MODEL_NAME,
            "task_id": task_id,
            "doc_metadata": {
                "document_id": node_id,
                "user_id": request.user.id,
                "version_number": node.current_version.version_number,
            },
            "parse_settings":parse_settings
        }
        pipe = redis_client.pipeline()
        pipe.set(f"{VECTOR_OWNER_KEY}:{task_id}", request.user.id, 24 * 3600)
        pipe.set(f"{VECTOR_STATUS_KEY}:{task_id}", "initializing", 24 * 3600)
        pipe.execute()
        if NodeVectorUsage.objects.filter(document_id=node_id).exists():
            current_app.delay(
                "vectorise_service.replace_document",
                args=[data]
            )
            return Response({"status": "Pending", "job_id": task_id}, status=status.HTTP_202_ACCEPTED)
        current_app.delay(
            "vectorise_service.vectorise_file",
            args=[data, [], True]
        )
        return Response({"status": "Pending", "job_id": task_id}, status=status.HTTP_202_ACCEPTED)



class VTaskResultView(APIView):
    authentication_classes = [
        XSessionTokenAuthentication
    ]
    permission_classes = [
        IsAuthenticated
    ]
    def get(self, request, task_id):
        user_id = request.user.id
        owner = redis_client.hget(VECTOR_OWNER_KEY, task_id)
        
        if owner is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if str(owner.decode() if isinstance(owner, bytes) else owner) != str(user_id):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        task_status = redis_client.hget(VECTOR_STATUS_KEY, task_id)
        if task_status is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        data = {
            "task_id": task_id,
            "status": task_status,
        }

        return Response(data=data)