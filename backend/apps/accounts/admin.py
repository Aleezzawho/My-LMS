from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import OtpRequest, Profile, RefreshSession, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-date_joined",)
    list_display = ("phone", "email", "is_active", "is_staff", "date_joined")
    list_filter = ("is_active", "is_staff", "groups")
    search_fields = ("phone", "email", "profile__display_name", "profile__handle")
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Contact", {"fields": ("email", "email_verified_at")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("phone", "email", "password1", "password2")}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "handle", "theme")
    search_fields = ("user__phone", "display_name", "handle")


@admin.register(OtpRequest)
class OtpRequestAdmin(admin.ModelAdmin):
    list_display = ("phone", "purpose", "attempts", "expires_at", "consumed_at", "created_at")
    list_filter = ("purpose",)
    search_fields = ("phone",)
    readonly_fields = ("code_hash", "delivery_ref")

    def has_add_permission(self, request):
        return False


@admin.register(RefreshSession)
class RefreshSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "jti", "created_at", "expires_at", "revoked_at", "revoked_reason")
    list_filter = ("revoked_reason",)
    search_fields = ("user__phone", "jti")
    readonly_fields = ("jti", "family", "parent", "created_at")

    def has_add_permission(self, request):
        return False
