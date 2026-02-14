from rest_framework.generics import RetrieveAPIView
from drive.serializers.node_serializers import NodeDetailsSerializer
from rest_framework.permissions import IsAuthenticated
from allauth.headless.contrib.rest_framework.authentication import XSessionTokenAuthentication
from django.shortcuts import get_object_or_404
from drive.models import Node
from drive.utils.permissions import IsEditor


class NodeDetails(RetrieveAPIView):
    authentication_classes = [
        XSessionTokenAuthentication
    ]
    permission_classes = [
        IsAuthenticated, IsEditor
    ]
    serializer_class = NodeDetailsSerializer

    def get_object(self):
        node_id = self.kwargs.get("pk")
        node = get_object_or_404(
            Node.active_objects.select_related("owner", "current_version"),
            pk=node_id
        )
        self.check_object_permissions(self.request, node)
        return node