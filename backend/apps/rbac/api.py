"""Admin-only endpoints for granting object-level capabilities."""

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from ninja import Router
from pydantic import BaseModel

from apps.accounts.auth import auth
from apps.common.errors import ApiError
from apps.rbac.models import ObjectPermission, Role
from apps.rbac.permissions import require_admin

router = Router(tags=["rbac"], auth=auth)
User = get_user_model()

MODEL_LABELS = {
    "track": ("catalog", "Track"),
    "contest": ("contests", "Contest"),
}


class GrantIn(BaseModel):
    user_id: str
    capability: str
    target_type: str
    target_id: int


class GrantOut(BaseModel):
    id: int
    user_id: str
    capability: str
    target_type: str
    target_id: int


class RoleAssignIn(BaseModel):
    role: str


@router.post("/grants", response={201: GrantOut})
def grant(request: HttpRequest, payload: GrantIn):
    require_admin(request.auth)
    if payload.capability not in ObjectPermission.Capability.values:
        raise ApiError(422, "invalid_capability", "Unknown capability.")
    if payload.target_type not in MODEL_LABELS:
        raise ApiError(422, "invalid_target", "Unknown target type.")
    app_label, model_name = MODEL_LABELS[payload.target_type]
    content_type = ContentType.objects.filter(app_label=app_label, model=model_name.lower()).first()
    if content_type is None:
        raise ApiError(503, "target_not_installed", "Target model is not installed yet.")
    user = User.objects.filter(public_id=payload.user_id).first()
    if user is None:
        raise ApiError(404, "user_not_found", "User not found.")
    model = content_type.model_class()
    if model is None or not model.objects.filter(pk=payload.target_id).exists():
        raise ApiError(404, "target_not_found", "Target object not found.")
    grant_obj, _ = ObjectPermission.objects.get_or_create(
        user=user,
        capability=payload.capability,
        content_type=content_type,
        object_id=payload.target_id,
        defaults={"granted_by": request.auth},
    )
    return 201, GrantOut(
        id=grant_obj.pk,
        user_id=str(user.public_id),
        capability=grant_obj.capability,
        target_type=payload.target_type,
        target_id=grant_obj.object_id,
    )


@router.delete("/grants/{grant_id}", response={204: None})
def revoke(request: HttpRequest, grant_id: int):
    require_admin(request.auth)
    deleted, _ = ObjectPermission.objects.filter(pk=grant_id).delete()
    if not deleted:
        raise ApiError(404, "not_found", "Grant not found.")
    return 204, None


@router.get("/grants", response=list[GrantOut])
def list_grants(request: HttpRequest, user_id: str | None = None):
    require_admin(request.auth)
    qs = ObjectPermission.objects.select_related("user", "content_type").order_by("-created_at")
    if user_id:
        qs = qs.filter(user__public_id=user_id)
    return [
        GrantOut(
            id=row.pk,
            user_id=str(row.user.public_id),
            capability=row.capability,
            target_type=row.content_type.model,
            target_id=row.object_id,
        )
        for row in qs[:200]
    ]


@router.post("/users/{user_id}/roles", response={204: None})
def assign_role(request: HttpRequest, user_id: str, payload: RoleAssignIn):
    """Roles are Django groups; this is the only way non-admins get one."""
    require_admin(request.auth)
    if payload.role not in Role.values:
        raise ApiError(422, "invalid_role", "Unknown role.")
    user = User.objects.filter(public_id=user_id).first()
    if user is None:
        raise ApiError(404, "user_not_found", "User not found.")
    from django.contrib.auth.models import Group

    group, _ = Group.objects.get_or_create(name=payload.role)
    user.groups.add(group)
    return 204, None
