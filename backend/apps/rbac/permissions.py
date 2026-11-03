from django.contrib.auth.models import AnonymousUser

from apps.common.errors import ApiError

from .models import ObjectPermission, Role


def is_admin(user) -> bool:
    return bool(
        getattr(user, "is_authenticated", False)
        and (getattr(user, "is_superuser", False) or getattr(user, "is_staff", False))
    )


def has_role(user, role: str) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if is_admin(user):
        return True
    return user.groups.filter(name=role).exists()


def can_edit_track(user, track) -> bool:
    if is_admin(user):
        return True
    if not getattr(user, "is_authenticated", False):
        return False
    return has_capability(user, track, ObjectPermission.Capability.EDIT)


def has_capability(user, obj, capability: str) -> bool:
    if is_admin(user):
        return True
    if not getattr(user, "is_authenticated", False) or obj is None:
        return False
    from django.contrib.contenttypes.models import ContentType

    return ObjectPermission.objects.filter(
        user=user,
        capability=capability,
        content_type=ContentType.objects.get_for_model(obj),
        object_id=obj.pk,
    ).exists()


def require_creator(user):
    if not (has_role(user, Role.CREATOR) or is_admin(user)):
        raise ApiError(403, "forbidden", "Creator role required.")
    return user


def require_admin(user):
    if not is_admin(user):
        raise ApiError(403, "forbidden", "Admin role required.")
    return user


def require_authenticated(user):
    if isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        raise ApiError(401, "unauthenticated", "Sign in required.")
    if not user.is_active:
        raise ApiError(401, "account_disabled", "Account is disabled.")
    return user
