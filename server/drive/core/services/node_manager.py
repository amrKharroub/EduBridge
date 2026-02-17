from guardian.shortcuts import get_objects_for_user, get_users_with_perms, assign_perm
from django.core.exceptions import BadRequest
from django.contrib.auth.models import User
from drive.models import Node
from django.shortcuts import get_object_or_404
from drive.utils.shortcuts import get_or_create_root_folder
from drive.core.services.redis_cache import redis_client, TASK_OWNER_KEY
from django.db import transaction
from django.db.models import F
from drive.utils.shortcuts import get_or_create_root_folder, update_user_storage_usage
from drive.core.tasks import generate_and_upload_zip_task
from drive.models import Node, NodeVersion, ZipFolder
from django.shortcuts import get_object_or_404
from django.core.exceptions import BadRequest, PermissionDenied
from rest_framework.exceptions import NotFound
from drive.utils.permissions import can_edit, can_view
from drive.core.services.azure_blob import generate_upload_sas, get_file_metadata, generate_download_sas
import uuid
from django.contrib.postgres.search import SearchQuery, SearchRank
from drive.utils.permissions import get_accessible_path_filter


def build_storage_key(user_id, node_id):
    return f"u/{user_id}/n/{node_id}/{uuid.uuid4().hex}"

def get_top_level_shared_nodes(user):
    """
    Get only top-level nodes (depth=1) that are shared with user
    """
    all_shared = get_objects_for_user(
        user,
        ['drive.view_node', 'drive.edit_node'],
        klass=Node.active_objects,
        any_perm=True,
        with_superuser=False,
        accept_global_perms=False
    )
    sorted_nodes = sorted(all_shared, key=lambda x: x.path)
    top_level = []
    for node in sorted_nodes:
        if not top_level or not node.path.startswith(top_level[-1].path):
            top_level.append(node)
    return top_level


def share_node_with_users(node, emails, access_level):
    users = User.objects.filter(email__in=emails)
    if users.count() != len(emails):
        raise BadRequest("not all emails are presint")
    if access_level == "viewer":
        have_perm_users = get_users_with_perms(node, only_with_perms_in=["view_node"])
        users = users.exclude(id__in=have_perm_users.values_list("id", flat=True))
        assign_perm("fileSharing.view_node", users, node)
    elif access_level == "editor":
        have_perm_users = get_users_with_perms(node, only_with_perms_in=["edit_node"])
        users = users.difference(have_perm_users)
        assign_perm("fileSharing.edit_node", users, node)


def create_folder_node(user: User, parent_id, folder_name) -> Node:
    if parent_id:
        parent_node = get_object_or_404(Node.active_objects, pk=parent_id)
    else:
        parent_node = get_or_create_root_folder(user)
    if not parent_node.is_folder and parent_node.status == Node.NodeStatus.ACTIVE:
        raise BadRequest("Invalid parent id")
    new_folder = Node(
        name=folder_name,
        owner=user,
        status=Node.NodeStatus.ACTIVE,
        type=Node.NodeType.folder
    )
    return parent_node.add_child(instance=new_folder)



def download_node(user, node_id):
    node = get_object_or_404(Node.active_objects.select_related("current_version"), pk=node_id)
    if not node.is_public and not can_view(user, node) and not can_edit(user, node):
        raise PermissionDenied()
    if node.is_folder:
        files_info, size = get_files_info(node)
        storage_key = build_storage_key(user.id, node.id) + "/" + node.name + ".zip"
        zipfolder = ZipFolder.objects.create(
            node=node,
            storage_key=storage_key,
            size=size
        )
        task = generate_and_upload_zip_task.delay(zipfolder.id, storage_key, node.name, files_info)
        redis_client.hset(TASK_OWNER_KEY, task.id, user.id)
        return {
            "status": "Zipping files",
            "task_id": task.id
        }
    else:
        download_sas_url = generate_download_sas(blob_ref=node.current_version.storage_key)
        return {
            "status": "done",
            "filename": node.name,
            "download_url": download_sas_url
        }
    

def get_files_info(node):
    children = node.get_descendants().filter(
        deleted_at__isnull = True,
        status = Node.NodeStatus.ACTIVE
    ).annotate(
        rel_storage_key=F("current_version__storage_key"),
        rel_size=F("current_version__size")
    ).only("id", "name", "path", "type")

    path_to_name = {
        child.path: child.name for child in children
    }

    path_to_name[node.path] = node.name

    steplen = node.steplen
    root_depth = node.depth

    file_info = []
    size = 0
    for child in children:
        if child.is_folder:
            continue
        size += child.rel_size
        chunks = [
            child.path[i:i + steplen]
            for i in range(root_depth * steplen, len(child.path), steplen)
        ]

        current = node.path
        parts = []
        for chunk in chunks:
            current += chunk
            parts.append(path_to_name[current])

        relative_name_path = "/".join(parts)

        file_info.append(
            (child.rel_storage_key, relative_name_path)
        )
    return file_info, size


def search_for_node(user, query_text):
    search_query = SearchQuery(query_text)
    security_fence = get_accessible_path_filter(user)

    results = Node.active_objects.filter(security_fence).annotate(
        rank=SearchRank("search_vector", search_query)
    ).filter(
        search_vector=search_query
    ).select_related("owner").order_by("-rank", "title")
    return results


def init_upload_process(*, user, parent_id, filename, size, mime_type, checksum):
    if parent_id is None:
        parent_node = get_or_create_root_folder(user)
    else:
        parent_node = get_object_or_404(Node.active_objects, pk=parent_id)
    if not parent_node.is_folder:
        raise BadRequest("Invalid parent id")
    if not can_edit(user, parent_node):
        raise PermissionDenied()
    with transaction.atomic():
        new_node = Node(
            owner = user,
            name = filename,
            type = Node.NodeType.file,
            status = Node.NodeStatus.UPLOADING,
        )
        parent_node.add_child(instance=new_node)

        storage_key = build_storage_key(user.pk, new_node.pk)
        node_version = NodeVersion.objects.create(
            node = new_node,
            storage_key = storage_key,
            size = size,
            mime_type = mime_type,
            checksum = checksum
        )

    upload_url = generate_upload_sas(
        blob_ref=storage_key,
        content_type=mime_type
    )

    return {
        "node_id": new_node.pk,
        "version_id": node_version.pk,
        "upload_url": upload_url
    }


def finalize_upload_process(*, user, version_id, node_id):
    node = get_object_or_404(Node.active_objects, pk=node_id)
    version = get_object_or_404(NodeVersion, pk=version_id)
    if node.owner != user:
        raise PermissionDenied()
    if node.status != Node.NodeStatus.UPLOADING:
        raise BadRequest
    
    meta = get_file_metadata(version.storage_key)
    if not meta['status']:
        with transaction.atomic():
            node.status = Node.NodeStatus.DRAFT
            node.save()
            version.status = NodeVersion.FileStatus.FAILED
            version.save()
        raise NotFound("File Not Found in Storage")
    if (
        meta["size"] == 0
        or meta["size"] != version.size
        or meta["type"] != version.mime_type 
        or (
            meta["content_md5"] is not None 
            and meta["content_md5"].hex() != version.checksum
        )
    ):
        with transaction.atomic():
            node.status = Node.NodeStatus.DRAFT
            node.save()
            version.status = NodeVersion.FileStatus.FAILED
            version.save()
        raise BadRequest("incomplete file upload")
    with transaction.atomic():
        version.status = NodeVersion.FileStatus.ACTIVE
        version.save()
        node.status = Node.NodeStatus.ACTIVE
        node.current_version = version
        node.save()
        update_user_storage_usage(user, version.size)
    return {
        "filename": node.name,
        "mime_type": version.mime_type
    }