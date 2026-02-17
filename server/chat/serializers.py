from rest_framework import serializers
from .models import Chat

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'thread_id', 'title', 'created_at', 'updated_at']
        read_only_fields = ['thread_id', 'created_at', 'updated_at']

class MessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['user', 'assistant'])
    content = serializers.CharField()
    timestamp = serializers.DateTimeField(read_only=True)  # could be from checkpoint metadata

class SendMessageSerializer(serializers.Serializer):
    message = serializers.CharField()