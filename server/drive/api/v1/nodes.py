from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drive.models import Node
from drive.serializers.node_serializers import (
    NodeDetailsSerializer,
    NodeSerializer,
    NodeShareSerializer,
    CreateFolderNodeSerializer,
    InitUploadSerializer,
    FinalizeFileUploadSerializer
)
from drive.utils.permissions import IsEditor, IsViewer
from drive.utils.shortcuts import get_or_create_root_folder
from drive.core.services.node_manager import (
    get_top_level_shared_nodes,
    share_node_with_users,
    create_folder_node,
    download_node,
    search_for_node,
    init_upload_process,
    finalize_upload_process
)
from rest_framework.response import Response
from django.core.exceptions import BadRequest
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action


class NodeViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'retrieve']:
            permission_classes = [IsAuthenticated, IsEditor]
        else:
            permission_classes = [IsAuthenticated, IsViewer]
        return [permission() for permission in permission_classes]
    
    def get_object(self, use_select_related=True):
        queryset = Node.active_objects
        if use_select_related:
            queryset = queryset.select_related("owner", "current_version")
        obj = get_object_or_404(
            queryset,
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
    
    @action(detail=False, methods=['get'])
    def shared(self, request):
        """GET /nodes/shared/ name=node-shared"""
        nodes = get_top_level_shared_nodes(request.user)
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsEditor])
    def share(self, request, pk=None):
        """POST /nodes/{id}/share/ name=node-share"""
        serializer = NodeShareSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        node = self.get_object(False)
        share_node_with_users(
            node,
            serializer.validated_data["emails"],
            serializer.validated_data["access_level"]
        )
        return Response(status=201)
    
    def create(self, request):
        serializer = CreateFolderNodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        folder = create_folder_node(
            request.user,
            serializer.validated_data["parent_id"],
            serializer.validated_data["name"]
        )
        serialized = NodeSerializer(folder)
        return Response(data=serialized.data, status=201)

class DownloadNodeView(APIView):
    def get(self, request, node_id):
        result = download_node(request.user, node_id)
        return Response(data=result, status=status.HTTP_202_ACCEPTED)
    

class SearchUserNode(APIView):
    def get(self, request):
        query_text = request.GET.get("q", "")
        result = search_for_node(request.user, query_text)
        return Response(data=result, status=status.HTTP_200_OK)
    

class InitFileUpload(APIView):
    def post(self, request):
        serializer = InitUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = init_upload_process(
            user=request.user,
            parent_id=serializer.validated_data['parent_id'],
            filename=serializer.validated_data['filename'],
            size=serializer.validated_data['size'],
            mime_type=serializer.validated_data['mime_type'],
            checksum=serializer.validated_data['checksum']
        )
        return Response(data=res, status=200)
    

class FinalizeFileUpload(APIView):
    def post(self, request, node_id):
        serializer = FinalizeFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = finalize_upload_process(
            user=request.user,
            version_id=serializer.validated_data["version_id"],
            node_id=node_id
        )
        return Response(data=res, status=201)