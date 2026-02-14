from rest_framework.permissions import BasePermission
from guardian.shortcuts import get_objects_for_user

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