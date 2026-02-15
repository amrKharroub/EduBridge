from django.urls import path, include
from drive.api.v1.nodes import NodeViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'nodes', NodeViewSet, basename='node')

urlpatterns = [
    path('api/', include(router.urls)),
]

# urlpatterns = [
#     path("nodes/<int:pk>/details", NodeDetails.as_view(), name="details-node"),
# ]