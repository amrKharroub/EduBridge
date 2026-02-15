from rest_framework.generics import RetrieveAPIView
from drive.serializers.node_serializers import NodeDetailsSerializer, NodeSerializer
from rest_framework.permissions import IsAuthenticated
from allauth.headless.contrib.rest_framework.authentication import XSessionTokenAuthentication
from django.shortcuts import get_object_or_404
from drive.models import Node
from drive.utils.permissions import IsEditor, IsViewer
from drive.utils.shortcuts import get_or_create_root_folder
from rest_framework.response import Response
from django.core.exceptions import BadRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
    


class NodeViewSet(viewsets.ModelViewSet):

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'retrieve']:
            permission_classes = [IsAuthenticated, IsEditor]
        else:
            permission_classes = [IsAuthenticated, IsViewer]
        return [permission() for permission in permission_classes]
    
    def get_object(self):
        obj = get_object_or_404(
            Node.active_objects.select_related("owner", "current_version"),
            pk=self.kwargs["pk"]
        )
        self.check_object_permissions(self.request, obj)
        return obj
    
    def get_queryset(self):
        user = self.request.user
        parent_id = self.request.query_params.get('parent_id', None)
        if parent_id:
            parent = get_object_or_404(Node.active_objects, pk=parent_id, owner=user)
            if not parent.is_folder:
                raise BadRequest("ivalid node id")
        else:
            parent = get_or_create_root_folder(self.request.user)
        return parent.get_children().filter(status=Node.NodeStatus.ACTIVE, deleted_at__isnull = True)

    def retrieve(self, request, pk=None):
        """GET /api/nodes/{pk}/ name=node-detail"""
        node = self.get_object()
        serializer = NodeDetailsSerializer(node)
        return Response(serializer.data)
    
    def list(self, request):
        """GET api/nodes name=node-list"""
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = NodeSerializer(qs, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = NodeSerializer(qs, many=True)
        return Response(serializer.data)


# class NodeViewSet(viewsets.ModelViewSet):
#     queryset = Node.active_objects.all()
#     # Your settings.py handles the default Authentication/Permissions

#     def get_queryset(self):
#         """
#         Handles 'List My Nodes' by default.
#         """
#         user = self.request.user
#         parent_id = self.request.query_params.get('parent_id')
        
#         # Filter logic for 'My Drive'
#         qs = Node.active_objects.filter(owner=user)
#         if parent_id:
#             return qs.filter(parent_id=parent_id)
#         return qs.filter(parent__isnull=True) # Root level

#     def get_serializer_class(self):
#         """
#         Map different actions to different serializers.
#         """
#         mapping = {
#             'retrieve': NodeDetailsSerializer,
#             # 'update': UpdateNodeMetadataSerializer,
#             # 'partial_update': UpdateNodeMetadataSerializer,
#             # 'shared': NodeSerializer,
#             # 'upload': FileUploadSerializer,
#             # 'share': NodeShareSerializer,
#         }
#         return mapping.get(self.action, None )#NodeSerializer)

#     # --- Custom Actions ---

#     @action(detail=False, methods=['get'])
#     def shared(self, request):
#         """GET /nodes/shared/"""
#         # Your logic for fetching nodes where user is in the share-list
#         nodes = get_nodes_shared_with_user(request.user) 
#         serializer = self.get_serializer(nodes, many=True)
#         return Response(serializer.data)

#     @action(detail=False, methods=['post'])
#     def upload(self, request):
#         """POST /nodes/upload/"""
#         # logic for Azure Blob upload + Node creation
#         return Response({"status": "upload successful"}, status=201)

#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsEditor])
#     def share(self, request, pk=None):
#         """POST /nodes/{id}/share/"""
#         node = self.get_object()
#         # logic: share_node_with_users(...)
#         return Response(status=200)

#     @action(detail=True, methods=['get'])
#     def download(self, request, pk=None):
#         """GET /nodes/{id}/download/"""
#         node = self.get_object()
#         # logic: generate_sas_token(node.blob_path)
#         link = "https://azure.storage.com/file?sas_token=..."
#         return Response({"download_url": link})