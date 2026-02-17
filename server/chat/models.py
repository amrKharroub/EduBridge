from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Chat(models.Model):
    AGENT_TYPES = (
        ('rag', 'RAG Chat'),
        ('quiz', 'Quiz Creator'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    thread_id = models.CharField(max_length=255, unique=True, db_index=True)
    agent_type = models.CharField(max_length=20, choices=AGENT_TYPES, default='rag')
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat {self.thread_id} ({self.agent_type}) - {self.user.username}"