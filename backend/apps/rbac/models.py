from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.common.models import TimeStampedModel


class Role(models.TextChoices):
    STUDENT = "student", "Student"
    CREATOR = "creator", "Content creator"
    ADMIN = "admin", "Admin"


class ObjectPermission(TimeStampedModel):
    """Per-object capability grant (tracks now, contests later).

    Deliberately generic so `rbac` never imports a domain app. Admins bypass it;
    everyone else gets exactly the capabilities listed here.
    """

    class Capability(models.TextChoices):
        EDIT = "edit", "Edit"
        PUBLISH = "publish", "Publish"
        SUPERVISE = "supervise", "Supervise"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="object_permissions"
    )
    capability = models.CharField(max_length=16, choices=Capability.choices)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    target = GenericForeignKey("content_type", "object_id")
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_permissions",
    )

    class Meta:
        db_table = "rbac_object_permission"
        indexes = [models.Index(fields=["content_type", "object_id"])]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "capability", "content_type", "object_id"],
                name="uniq_object_permission",
            )
        ]
