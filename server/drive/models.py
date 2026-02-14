from django.db import models
from treebeard.mp_tree import MP_Node, MP_NodeManager
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
    
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull = True)
    
class SoftDeleteNodeManager(MP_NodeManager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull = True, status=Node.NodeStatus.ACTIVE)
    
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    active_objects = SoftDeleteManager()

    class Meta:
        abstract = True


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Node(MP_Node):
    class NodeType(models.TextChoices):
        file = "file", "File"
        folder = "folder", "Folder"

    class NodeStatus(models.TextChoices):
        UPLOADING = "UPLOADING"
        ACTIVE = "ACTIVE"
        TRASHED = "TRASHED"
        DRAFT = "DRAFT"
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="nodes")
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=6, choices=NodeType.choices)
    tags = models.ManyToManyField("Tag", blank=True)
    is_public = models.BooleanField(default=False)
    description = models.TextField()
    
    status = models.CharField(
        max_length=10,
        choices=NodeStatus.choices,
        default=NodeStatus.UPLOADING,
        db_index=True
    )
    current_version = models.OneToOneField(
        "NodeVersion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_version"
    )
    search_vector = SearchVectorField(null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    node_order_by = ['name']

    active_objects = SoftDeleteNodeManager()

    @property
    def is_folder(self):
        return self.type == self.NodeType.folder
    
    class Meta:
        permissions = [
            ("edit_node", "Can edit the node, view, change, add, delete node")
        ]
        indexes = [
            GinIndex(fields=["search_vector"]),
        ]

    def __str__(self):
        return f"{self.name}"
    


class NodeVersion(TimeStampedModel):
    class FileStatus(models.TextChoices):
        UPLOADING = "UPLOADING"
        ACTIVE = "ACTIVE"
        FAILED = "FAILED"

    class StorageProvider(models.TextChoices):
        AZURE = "azure", "Azure Blob Storage"
        AWS = "aws", "AWS S3"
        LOCAL = "local", "Local Storage"

    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveSmallIntegerField()
    storage_provider = models.CharField(max_length=128, choices=StorageProvider.choices, default=StorageProvider.AZURE)
    storage_key = models.CharField(max_length=512, unique=True)

    size = models.PositiveBigIntegerField(help_text="Size of the file in bytes")
    mime_type = models.CharField(max_length=124, help_text="The IANA media type of the file")
    checksum = models.CharField(max_length=64, help_text="MD5 hash of the file")

    status = models.CharField(
        max_length=10,
        choices=FileStatus.choices,
        default=FileStatus.UPLOADING,
        db_index=True
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            with transaction.atomic():
                parent = Node.objects.select_for_update().get(pk=self.node_id)
                last_num = NodeVersion.active_objects.filter(node=parent).aggregate(
                    models.Max("version_number")
                )["version_number__max"] or 0
                self.version_number = last_num + 1
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    class Meta:
        ordering = ['-version_number']
        constraints = [
            models.UniqueConstraint(
                fields=["node", "version_number"],
                name="unique_node_version"
            ),
            models.UniqueConstraint(
                fields=["storage_provider", "storage_key"],
                name="unique_file_place"
            ),
        ]

class StorageUsage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="storage_usage")
    used_bytes = models.PositiveBigIntegerField(default=0, help_text="Cumulative file sizes in bytes")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.used_bytes} bytes"
    

class ZipFolder(models.Model):
    class ZipFolderStatus(models.TextChoices):
        PENDING = "PENDING"
        COMPLETED = "COMPLETED"
        DELETED = "DELETED"
        FAILED = "FAILED"

    node = models.ForeignKey(Node, on_delete=models.SET_NULL, related_name="downloaded_folder", null=True)
    size = models.PositiveBigIntegerField(help_text="Size of the precompressed zipped file in bytes")
    storage_key = models.CharField(max_length=512, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=ZipFolderStatus.choices, default=ZipFolderStatus.PENDING, db_index=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            with transaction.atomic():
                self.expires_at = timezone.now() + timedelta(hours=24)
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
