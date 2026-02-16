from rest_framework.permissions import BasePermission
from guardian.shortcuts import get_objects_for_user
from django.contrib.auth.models import User
from drive.models import Node

class IsEditor(BasePermission):
    """
    Object-level permission to only allow editors of a node (or its ancestors)
    to edit it.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if obj.owner == user:
            return True
        
        if user.has_perm("drive.edit_node", obj):
            return True
        
        ancestors_qs = obj.get_ancestors()
        return get_objects_for_user(
            user, 
            "drive.edit_node", 
            klass=ancestors_qs
        ).exists()

class IsViewer(BasePermission):
    """
    Object-level permission to allow viewing if the user has view_node 
    perms on the node or ancestors.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj.owner == user:
            return True
            
        if user.has_perm("drive.view_node", obj):
            return True
            
        ancestors_qs = obj.get_ancestors()
        return get_objects_for_user(
            user, 
            "drive.view_node", 
            klass=ancestors_qs
        ).exists()
    

def can_edit(user: User, node: Node):
    if node.owner == user:
        return True
    
    if user.has_perm("fileSharing.edit_node", node):
        return True
    
    ancestors_qs = node.get_ancestors()
    permitted_nodes = get_objects_for_user(
        user, 
        "fileSharing.edit_node", 
        klass=ancestors_qs
    )
    return permitted_nodes.exists()

def can_view(user: User, node: Node):
    if node.owner == user:
        return True
    
    if user.has_perm("fileSharing.view_node", node):
        return True
    
    ancestors_qs = node.get_ancestors()
    permitted_nodes = get_objects_for_user(
        user, 
        "fileSharing.view_node", 
        klass=ancestors_qs
    )
    return permitted_nodes.exists()