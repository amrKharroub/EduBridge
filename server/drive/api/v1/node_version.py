from rest_framework.generics import ListAPIView
from allauth.headless.contrib.rest_framework.authentication import XSessionTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drive.models import Node, NodeVersion
from drive.serializers.node_version_serializers import NodeVersionSerializer
from drive.utils.permissions import can_view
from django.core.exceptions import PermissionDenied, BadRequest
from rest_framework.response import Response

class NodeVersionsListView(ListAPIView):
    authentication_classes = [
        XSessionTokenAuthentication
    ]
    permission_classes = [
        IsAuthenticated
    ]
    serializer_class = NodeVersionSerializer

    def get_queryset(self):
        node_id = self.kwargs.get("node_id")
        node = get_object_or_404(Node.active_objects, pk=node_id)
        if node.is_folder:
            raise BadRequest("no versions for folders")
        if not node.is_public and not can_view(self.request.user, node):
            raise PermissionDenied("You don't have viewing permissions")
        return NodeVersion.active_objects.filter(node=node, status=NodeVersion.FileStatus.ACTIVE)
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "versions": response.data
        })