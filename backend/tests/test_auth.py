import pytest
from django.utils import timezone

from apps.accounts.models import OtpRequest, RefreshSession
from apps.accounts.phones import normalize_phone

pytestmark = pytest.mark.django_db


def post(client, path, payload, csrf=None):
    headers = {}
    if csrf:
        headers["HTTP_X_CSRF_TOKEN"] = csrf
    return client.post(path, payload, content_type="application/json", **headers)


class TestPhoneNormalization:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("09121234567", "+989121234567"),
            ("+989121234567", "+989121234567"),
            ("00989121234567", "+989121234567"),
            ("9121234567", "+989121234567"),
            ("0912 123 4567", "+989121234567"),
        ],
    )
    def test_accepts_common_formats(self, raw, expected):
        assert normalize_phone(raw) == expected

    @pytest.mark.parametrize("raw", ["", "12345", "08121234567", "+1234567890", "abcdefghijk"])
    def test_rejects_invalid(self, raw):
        with pytest.raises(ValueError):
            normalize_phone(raw)


class TestOtpFlow:
    def test_request_and_verify_creates_user(self, api_client, sms_outbox):
        response = post(api_client, "/api/v1/auth/otp/request", {"phone": "09121234567"})
        assert response.status_code == 204
        assert len(sms_outbox) == 1
        code = sms_outbox[0]["code"]
        assert len(code) == 6 and code.isdigit()

        response = post(
            api_client, "/api/v1/auth/otp/verify", {"phone": "09121234567", "code": code}
        )
        assert response.status_code == 200
        body = response.json()
        assert body["user"]["phone"] == "+989121234567"
        assert body["user"]["roles"] == ["student"]
        assert body["access_token"]
        assert response.cookies["lms_refresh"]["httponly"]
        assert response.cookies["lms_access"]["httponly"]

    def test_otp_is_stored_hashed(self, api_client, sms_outbox):
        post(api_client, "/api/v1/auth/otp/request", {"phone": "09121234567"})
        code = sms_outbox[0]["code"]
        otp = OtpRequest.objects.get()
        assert code not in otp.code_hash
        assert otp.attempts == 0

    def test_code_cannot_be_replayed(self, api_client, sms_outbox):
        post(api_client, "/api/v1/auth/otp/request", {"phone": "09121234567"})
        code = sms_outbox[0]["code"]
        assert (
            post(
                api_client, "/api/v1/auth/otp/verify", {"phone": "09121234567", "code": code}
            ).status_code
            == 200
        )
        replay = post(api_client, "/api/v1/auth/otp/verify", {"phone": "09121234567", "code": code})
        assert replay.status_code == 400
        assert replay.json()["code"] == "otp_invalid"

    def test_wrong_code_increments_attempts_and_locks(self, api_client, sms_outbox):
        post(api_client, "/api/v1/auth/otp/request", {"phone": "09121234567"})
        wrong = "000000" if sms_outbox[0]["code"] != "000000" else "111111"
        for _ in range(5):
            response = post(
                api_client, "/api/v1/auth/otp/verify", {"phone": "09121234567", "code": wrong}
            )
            assert response.status_code in (400, 429)
        otp = OtpRequest.objects.get()
        assert otp.attempts == otp.max_attempts
        response = post(
            api_client,
            "/api/v1/auth/otp/verify",
            {"phone": "09121234567", "code": sms_outbox[0]["code"]},
        )
        assert response.status_code == 429
        assert response.json()["code"] in {"otp_locked", "rate_limited"}

    def test_resend_cooldown(self, api_client, sms_outbox):
        assert (
            post(api_client, "/api/v1/auth/otp/request", {"phone": "09121234567"}).status_code
            == 204
        )
        response = post(api_client, "/api/v1/auth/otp/request", {"phone": "09121234567"})
        assert response.status_code == 429
        assert response.json()["code"] == "otp_too_soon"
        assert len(sms_outbox) == 1

    def test_old_code_invalidated_on_new_request(self, api_client, sms_outbox):
        post(api_client, "/api/v1/auth/otp/request", {"phone": "09121234567"})
        first = sms_outbox[0]["code"]
        OtpRequest.objects.update(created_at=OtpRequest.objects.first().created_at)
        # Simulate the cooldown window having elapsed.
        from django.core.cache import cache

        cache.clear()
        post(api_client, "/api/v1/auth/otp/request", {"phone": "09121234567"})
        second = sms_outbox[1]["code"]
        assert (
            post(
                api_client, "/api/v1/auth/otp/verify", {"phone": "09121234567", "code": first}
            ).status_code
            == 400
        )
        if second != first:
            assert (
                post(
                    api_client, "/api/v1/auth/otp/verify", {"phone": "09121234567", "code": second}
                ).status_code
                == 200
            )

    def test_expired_code_rejected(self, api_client, sms_outbox):
        post(api_client, "/api/v1/auth/otp/request", {"phone": "09121234567"})
        code = sms_outbox[0]["code"]
        OtpRequest.objects.update(expires_at=timezone.now() - timezone.timedelta(seconds=1))
        response = post(
            api_client, "/api/v1/auth/otp/verify", {"phone": "09121234567", "code": code}
        )
        assert response.status_code == 400
        assert response.json()["code"] == "otp_expired"

    def test_invalid_phone_format(self, api_client):
        response = post(api_client, "/api/v1/auth/otp/request", {"phone": "12345"})
        assert response.status_code == 422
        assert response.json()["code"] in {"invalid_phone", "validation_error"}

    def test_send_does_not_leak_account_existence(self, api_client, sms_outbox):
        response = post(api_client, "/api/v1/auth/otp/request", {"phone": "09999999999"})
        assert response.status_code == 204


class TestPasswordLogin:
    def test_login_sets_cookies(self, api_client, user):
        response = post(
            api_client,
            "/api/v1/auth/login",
            {"phone": user.phone, "password": "correct-horse-battery"},
        )
        assert response.status_code == 200
        assert response.json()["user"]["has_password"] is True
        assert response.cookies["lms_refresh"]["path"] == "/api/v1/auth"
        assert "Secure" in response.cookies["lms_refresh"].coded_value or response.cookies[
            "lms_refresh"
        ].get("secure")

    def test_wrong_password(self, api_client, user):
        response = post(api_client, "/api/v1/auth/login", {"phone": user.phone, "password": "nope"})
        assert response.status_code == 401
        assert response.json()["code"] == "invalid_credentials"

    def test_unknown_phone_and_wrong_password_are_indistinguishable(self, api_client, user):
        a = post(api_client, "/api/v1/auth/login", {"phone": user.phone, "password": "nope"})
        b = post(api_client, "/api/v1/auth/login", {"phone": "09129999999", "password": "nope"})
        assert a.status_code == b.status_code == 401
        assert a.json()["code"] == b.json()["code"]

    def test_inactive_user_cannot_login(self, api_client, user):
        user.is_active = False
        user.save()
        response = post(
            api_client,
            "/api/v1/auth/login",
            {"phone": user.phone, "password": "correct-horse-battery"},
        )
        assert response.status_code == 401


class TestRefreshRotation:
    def _login(self, api_client, user):
        response = post(
            api_client,
            "/api/v1/auth/login",
            {"phone": user.phone, "password": "correct-horse-battery"},
        )
        return response.cookies["lms_csrf"].value, response.cookies["lms_refresh"].value

    def test_rotation_issues_new_session(self, api_client, user):
        csrf, refresh = self._login(api_client, user)
        response = post(api_client, "/api/v1/auth/refresh", {}, csrf=csrf)
        assert response.status_code == 200
        assert response.cookies["lms_refresh"].value != refresh
        assert RefreshSession.objects.filter(revoked_reason="rotated").count() == 1

    def test_refresh_requires_csrf(self, api_client, user):
        self._login(api_client, user)
        response = post(api_client, "/api/v1/auth/refresh", {})
        assert response.status_code == 403
        assert response.json()["code"] == "csrf_failed"

    def test_refresh_requires_matching_header(self, api_client, user):
        self._login(api_client, user)
        response = post(api_client, "/api/v1/auth/refresh", {}, csrf="wrong-value")
        assert response.status_code == 403

    def test_reuse_revokes_whole_family(self, api_client, user):
        csrf, old_refresh = self._login(api_client, user)
        first = post(api_client, "/api/v1/auth/refresh", {}, csrf=csrf)
        assert first.status_code == 200
        new_csrf = first.cookies["lms_csrf"].value
        new_refresh = first.cookies["lms_refresh"].value

        api_client.cookies["lms_refresh"] = old_refresh
        replay = post(api_client, "/api/v1/auth/refresh", {}, csrf=new_csrf)
        assert replay.status_code == 401
        assert replay.json()["code"] == "refresh_reused"

        api_client.cookies["lms_refresh"] = new_refresh
        after = post(api_client, "/api/v1/auth/refresh", {}, csrf=new_csrf)
        assert after.status_code == 401
        assert RefreshSession.objects.filter(revoked_at__isnull=True).count() == 0

    def test_logout_revokes_family_and_clears_cookies(self, api_client, user):
        csrf, _ = self._login(api_client, user)
        response = post(api_client, "/api/v1/auth/logout", {}, csrf=csrf)
        assert response.status_code == 204
        assert response.cookies["lms_access"].value == ""
        assert RefreshSession.objects.filter(revoked_at__isnull=True).count() == 0


class TestMe:
    def test_me_requires_auth(self, api_client):
        response = api_client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_me_with_cookie(self, auth_client):
        response = auth_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        assert response.json()["phone"] == "+989121234567"

    def test_me_with_bearer(self, api_client, user):
        login = post(
            api_client,
            "/api/v1/auth/login",
            {"phone": user.phone, "password": "correct-horse-battery"},
        )
        token = login.json()["access_token"]
        response = api_client.get("/api/v1/auth/me", HTTP_AUTHORIZATION=f"Bearer {token}")
        assert response.status_code == 200

    def test_revoked_session_blocks_access_token(self, auth_client):
        RefreshSession.objects.update(revoked_at=timezone.now())
        response = auth_client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_update_profile_requires_csrf(self, auth_client):
        response = auth_client.patch(
            "/api/v1/auth/me", {"display_name": "Sara"}, content_type="application/json"
        )
        assert response.status_code == 403

    def test_update_profile(self, auth_client):
        response = auth_client.patch(
            "/api/v1/auth/me",
            {"display_name": "Sara", "handle": "sara_dev"},
            content_type="application/json",
            HTTP_X_CSRF_TOKEN=auth_client.csrf_header,
        )
        assert response.status_code == 200
        assert response.json()["profile"]["handle"] == "sara_dev"

    def test_handle_uniqueness(self, auth_client, other_user):
        from apps.accounts.models import Profile

        Profile.objects.update_or_create(user=other_user, defaults={"handle": "taken"})
        response = auth_client.patch(
            "/api/v1/auth/me",
            {"handle": "taken"},
            content_type="application/json",
            HTTP_X_CSRF_TOKEN=auth_client.csrf_header,
        )
        assert response.status_code == 409

    def test_set_password_revokes_sessions(self, auth_client):
        response = auth_client.post(
            "/api/v1/auth/password",
            {"current_password": "correct-horse-battery", "new_password": "a-new-secret-42"},
            content_type="application/json",
            HTTP_X_CSRF_TOKEN=auth_client.csrf_header,
        )
        assert response.status_code == 204
        auth_client.user.refresh_from_db()
        assert auth_client.user.check_password("a-new-secret-42")
        assert RefreshSession.objects.filter(revoked_at__isnull=True).count() == 0

    def test_weak_password_rejected(self, auth_client):
        response = auth_client.post(
            "/api/v1/auth/password",
            {"current_password": "correct-horse-battery", "new_password": "123"},
            content_type="application/json",
            HTTP_X_CSRF_TOKEN=auth_client.csrf_header,
        )
        assert response.status_code == 422


class TestErrorEnvelope:
    def test_not_found_shape(self, api_client):
        response = api_client.get("/api/v1/auth/does-not-exist")
        assert response.status_code == 404
        body = response.json()
        assert set(body) >= {"code", "message", "details"}

    def test_validation_shape(self, api_client):
        response = post(api_client, "/api/v1/auth/login", {"phone": "x"})
        assert response.status_code == 422
        body = response.json()
        assert body["code"] == "validation_error"
        assert isinstance(body["details"], list)

    def test_request_id_header(self, api_client):
        response = api_client.get("/api/v1/auth/me")
        assert response.headers["X-Request-ID"]
