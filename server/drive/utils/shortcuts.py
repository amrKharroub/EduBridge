from django.contrib.auth.models import User
from ..models import Node, StorageUsage
from django.db import transaction

def get_or_create_root_folder(user:User) -> Node:
    if root := Node.active_objects.filter(owner=user, name=f"{user.pk}Home").first():
        return root
    with transaction.atomic():
        root = Node.add_root(
            owner = user,
            name = f"{user.pk}Home",
            type = Node.NodeType.folder,
            status = Node.NodeStatus.ACTIVE
        )
        StorageUsage.objects.get_or_create(user=user)
    return root