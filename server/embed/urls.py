from django.urls import path
from embed.views import VectoriseNode, VTaskResultView

urlpatterns = [
    path("vectorise/<int:node_id>/embed", VectoriseNode.as_view(), name="generate-embedding"),
    path("vectorise/tasks/<str:task_id>/", VTaskResultView.as_view(), name="vec-result"),
]