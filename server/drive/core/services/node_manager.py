from guardian.shortcuts import get_objects_for_user, get_users_with_perms, assign_perm
from django.core.exceptions import BadRequest
from django.contrib.auth.models import User
from drive.models import Node
from django.shortcuts import get_object_or_404
from drive.utils.shortcuts import get_or_create_root_folder

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