import uuid

import pytest
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from apps.accounts.models import User
from apps.common.errors import ApiError
from apps.rbac.models import ObjectPermission, Role
from apps.rbac.permissions import (
    has_capability,
    has_role,
    is_admin,
    require_admin,
    require_authenticated,
    require_creator,
)

pytestmark = pytest.mark.django_db


def login(client, user, password="correct-horse-battery"):
    response = client.post(
        "/api/v1/auth/login",
        {"phone": user.phone, "password": password},
        content_type="application/json",
    )
    assert response.status_code == 200, response.content
    csrf = response.cookies["lms_csrf"].value
    return csrf


class TestRoleChecks:
    def test_default_student_role_assigned_by_otp(self, api_client, sms_outbox):
        from apps.accounts.models import OtpRequest

        api_client.post(
            "/api/v1/auth/otp/request", {"phone": "09121112222"}, content_type="application/json"
        )
        code = sms_outbox[0]["code"]
        api_client.post(
            "/api/v1/auth/otp/verify",
            {"phone": "09121112222", "code": code},
            content_type="application/json",
        )
        user = User.objects.get(phone="+989121112222")
        assert list(user.groups.values_list("name", flat=True)) == [Role.STUDENT]

    def test_admin_short_circuits(self, admin_user):
        assert is_admin(admin_user)
        assert has_role(admin_user, Role.CREATOR)

    def test_plain_user_has_no_creator_role(self, user):
        assert not has_role(user, Role.CREATOR)
        with pytest.raises(ApiError) as exc:
            require_creator(user)
        assert exc.value.status_code == 403

    def test_group_grants_role(self, user):
        group, _ = Group.objects.get_or_create(name=Role.CREATOR)
        user.groups.add(group)
        assert has_role(user, Role.CREATOR)
        require_creator(user)

    def test_anonymous_rejected(self, django_user_model):
        from django.contrib.auth.models import AnonymousUser

        with pytest.raises(ApiError) as exc:
            require_authenticated(AnonymousUser())
        assert exc.value.status_code == 401

    def test_inactive_user_rejected(self, user):
        user.is_active = False
        with pytest.raises(ApiError):
            require_authenticated(user)

    def test_require_admin_blocks_students(self, user):
        with pytest.raises(ApiError) as exc:
            require_admin(user)
        assert exc.value.status_code == 403


class TestObjectCapabilities:
    def _object(self):
        """Use a content type that already exists; catalog.Track is not installed yet."""
        content_type = ContentType.objects.get_for_model(User)
        target = User.objects.create_user(phone="09125556666")
        return content_type, target

    def test_unrelated_user_lacks_capability(self, user):
        content_type, target = self._object()
        assert not has_capability(user, target, ObjectPermission.Capability.EDIT)

    def test_grant_confers_capability(self, user):
        content_type, target = self._object()
        ObjectPermission.objects.create(
            user=user,
            capability=ObjectPermission.Capability.EDIT,
            content_type=content_type,
            object_id=target.pk,
        )
        assert has_capability(user, target, ObjectPermission.Capability.EDIT)
        assert not has_capability(user, target, ObjectPermission.Capability.SUPERVISE)

    def test_capability_is_scoped_to_object(self, user):
        content_type, target = self._object()
        other_target = User.objects.create_user(phone="09127778888")
        ObjectPermission.objects.create(
            user=user,
            capability=ObjectPermission.Capability.EDIT,
            content_type=content_type,
            object_id=target.pk,
        )
        assert not has_capability(user, other_target, ObjectPermission.Capability.EDIT)

    def test_admin_bypasses_object_checks(self, admin_user):
        content_type, target = self._object()
        assert has_capability(admin_user, target, ObjectPermission.Capability.SUPERVISE)

    def test_duplicate_grant_rejected_by_db(self, user):
        from django.db import IntegrityError, transaction

        content_type, target = self._object()
        kwargs = dict(
            user=user,
            capability=ObjectPermission.Capability.EDIT,
            content_type=content_type,
            object_id=target.pk,
        )
        ObjectPermission.objects.create(**kwargs)
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                ObjectPermission.objects.create(**kwargs)


class TestRbacApi:
    def test_student_cannot_assign_roles(self, auth_client, other_user):
        response = auth_client.post(
            f"/api/v1/admin/rbac/users/{other_user.public_id}/roles",
            {"role": Role.CREATOR},
            content_type="application/json",
            HTTP_X_CSRF_TOKEN=auth_client.csrf_header,
        )
        assert response.status_code == 403
        assert other_user.groups.count() == 0

    def test_admin_can_assign_creator(self, admin_user, other_user):
        from django.test import Client

        client = Client()
        login(client, admin_user)
        response = client.post(
            f"/api/v1/admin/rbac/users/{other_user.public_id}/roles",
            {"role": Role.CREATOR},
            content_type="application/json",
        )
        assert response.status_code == 204
        assert other_user.groups.filter(name=Role.CREATOR).exists()

    def test_unknown_role_rejected(self, admin_user, other_user):
        from django.test import Client

        client = Client()
        login(client, admin_user)
        response = client.post(
            f"/api/v1/admin/rbac/users/{other_user.public_id}/roles",
            {"role": "god"},
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_grant_unknown_user(self, admin_user):
        from django.test import Client

        client = Client()
        login(client, admin_user)
        response = client.post(
            "/api/v1/admin/rbac/grants",
            {
                "user_id": str(uuid.uuid4()),
                "capability": "edit",
                "target_type": "track",
                "target_id": 1,
            },
            content_type="application/json",
        )
        assert response.status_code in (404, 503)


class TestHealth:
    def test_health_is_public(self, api_client):
        response = api_client.get("/api/v1/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["checks"] == {"db": True, "cache": True}
