from django.db import models
from django.contrib.auth.models import User
from drive.models import Node


class VectorStorageUsage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vector_usage")
    used_bytes = models.PositiveBigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)


class NodeVectorUsage(models.Model):
    document = models.OneToOneField(Node, on_delete=models.CASCADE)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    version_number = models.PositiveSmallIntegerField(default=1)
    vector_count = models.PositiveIntegerField(default=0, help_text="number of vectors stored for that document")
    text_size = models.PositiveBigIntegerField(default=0)
    total_usage = models.PositiveBigIntegerField(default=0)
