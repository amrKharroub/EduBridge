from django.urls import path
from drive.api.v1.nodes import NodeDetails


urlpatterns = [
    path("nodes/<int:pk>/details", NodeDetails.as_view(), name="details-node"),
]