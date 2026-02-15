from guardian.shortcuts import get_objects_for_user
from drive.models import Node

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