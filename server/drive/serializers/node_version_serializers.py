from drive.models import NodeVersion
from rest_framework import serializers

class NodeVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeVersion
        fields = ["id", "version_number", "size", "created_at", "updated_at"]