from django.urls import path, include
from drive.api.v1.nodes import NodeViewSet, InitFileUpload, FinalizeFileUpload
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'nodes', NodeViewSet, basename='node')

urlpatterns = [
    path('api/', include(router.urls)),
    path("nodes/files/upload-intent", InitFileUpload.as_view(), name="init-upload"),
    path("nodes/files/<int:node_id>/finalize", FinalizeFileUpload.as_view(), name="finalize-upload"),
]