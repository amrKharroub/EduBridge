from django.urls import path, include
from drive.api.v1.nodes import (
    NodeViewSet,
    InitFileUpload,
    FinalizeFileUpload,
    SearchUserNode,
    UpdateNode,
    DownloadNodeView
)
from drive.api.v1.node_version import NodeVersionsListView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'nodes', NodeViewSet, basename='node')

urlpatterns = [
    path('api/', include(router.urls)),
    path("api/nodes/files/upload-intent", InitFileUpload.as_view(), name="init-upload"),
    path("api/nodes/files/<int:node_id>/finalize", FinalizeFileUpload.as_view(), name="finalize-upload"),
    path("api/nodes/search/", SearchUserNode.as_view(), name="node-search"),
    path("nodes/<int:pk>/", UpdateNode.as_view(), name="update-node"),
    path("nodes/files/<int:node_id>/versions", NodeVersionsListView.as_view(), name="node-versions"),
    path("nodes/<int:node_id>/download", DownloadNodeView.as_view(), name="download-node"),
]