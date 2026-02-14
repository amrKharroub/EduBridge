from rest_framework import serializers
from guardian.shortcuts import get_users_with_perms
from django.contrib.auth.models import User
from drive.models import Node

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email")

class NodeDetailsSerializer(serializers.ModelSerializer):
    shared_with = serializers.SerializerMethodField()
    owner_email = serializers.ReadOnlyField(source="owner.email")
    version_number = serializers.ReadOnlyField(source="current_version.version_number")
    path = serializers.SerializerMethodField()

    class Meta:
        model = Node
        fields = ["name", "type", "owner_email", "version_number", "shared_with", "path"]

    def get_shared_with(self, obj):
        user_perms = get_users_with_perms(obj, attach_perms=True)
        result = []
        for user, perms in user_perms.items():
            user_data = SimpleUserSerializer(user).data
            result.append({
                "user": user_data,
                "perms": perms
            })
        return result
    
    def get_path(self, obj):
        ancestors = [item["name"] for item in list(obj.get_ancestors().values("name"))]
        return "/" + "/".join(ancestors[1:])