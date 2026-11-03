from django.contrib import admin

from .models import ObjectPermission


@admin.register(ObjectPermission)
class ObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ("user", "capability", "content_type", "object_id", "created_at")
    list_filter = ("capability", "content_type")
    search_fields = ("user__phone",)
    autocomplete_fields = ("user",)
