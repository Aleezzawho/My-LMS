"""Authentication endpoints: SMS OTP, password login, refresh rotation, profile."""

import secrets

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError, transaction
from django.http import HttpRequest
from django.utils import timezone
from ninja import Router, Status
from ninja.responses import Response

from apps.common.errors import ApiError
from apps.common.middleware import client_ip
from apps.common.ratelimit import check_rate_limit
from apps.rbac.models import Role
from apps.rbac.permissions import require_authenticated

from .auth import auth
from .models import OtpPurpose, Profile, RefreshSession
from .phones import normalize_phone
from .schemas import (
    MessageOut,
    OtpVerifyIn,
    PasswordLoginIn,
    PasswordSetIn,
    PhoneIn,
    ProfileOut,
    ProfileUpdateIn,
    SessionOut,
    TokenOut,
    UserOut,
)
from .services import tokens
from .services.otp import issue_otp, verify_otp
from .services.tokens import TokenPair, build_refresh_token

router = Router(tags=["auth"])

User = get_user_model()


def _roles(user) -> list[str]:
    return sorted(user.groups.values_list("name", flat=True))


def user_out(user) -> UserOut:
    profile = getattr(user, "profile", None) or Profile.objects.create(user=user)
    return UserOut(
        id=str(user.public_id),
        phone=user.phone,
        email=user.email,
        roles=_roles(user),
        profile=ProfileOut(
            display_name=profile.display_name,
            handle=profile.handle,
            bio=profile.bio,
            theme=profile.theme,
        ),
        date_joined=user.date_joined,
        has_password=user.has_usable_password(),
    )


def _set_auth_cookies(response: Response, pair: TokenPair) -> None:
    access_max_age = max(0, int((pair.access_expires_at - timezone.now()).total_seconds()))
    refresh_max_age = max(0, int((pair.refresh_session.expires_at - timezone.now()).total_seconds()))
    response.set_cookie(
        settings.ACCESS_COOKIE_NAME,
        pair.access_token,
        max_age=access_max_age,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite="Lax",
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME,
        build_refresh_token(pair.refresh_session),
        max_age=refresh_max_age,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite="Lax",
        domain=settings.COOKIE_DOMAIN,
        path=settings.REFRESH_COOKIE_PATH,
    )
    response.set_cookie(
        settings.CSRF_COOKIE_NAME,
        secrets.token_urlsafe(32),
        max_age=refresh_max_age,
        httponly=False,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite="Lax",
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    response["Cache-Control"] = "no-store"


def _clear_auth_cookies(response: Response) -> None:
    for name, path in (
        (settings.ACCESS_COOKIE_NAME, "/"),
        (settings.REFRESH_COOKIE_NAME, settings.REFRESH_COOKIE_PATH),
        (settings.CSRF_COOKIE_NAME, "/"),
    ):
        response.delete_cookie(name, domain=settings.COOKIE_DOMAIN, path=path, samesite="Lax")
    response["Cache-Control"] = "no-store"


def assert_csrf(request: HttpRequest) -> None:
    """Double-submit CSRF check for cookie-authenticated state changes."""
    if request.headers.get("Authorization"):
        return
    cookie = request.COOKIES.get(settings.CSRF_COOKIE_NAME, "")
    header = request.headers.get("X-CSRF-Token", "")
    if not cookie or not header or not secrets.compare_digest(cookie, header):
        raise ApiError(403, "csrf_failed", "Missing or invalid CSRF token.")


def _issued_response(pair: TokenPair) -> Response:
    payload = TokenOut(
        access_token=pair.access_token,
        expires_in=settings.ACCESS_TOKEN_TTL_SECONDS,
        user=user_out(pair.refresh_session.user),
    ).model_dump(mode="json")
    response = Response(payload, status=200)
    _set_auth_cookies(response, pair)
    return response


def _parse_phone(raw: str) -> str:
    try:
        return normalize_phone(raw)
    except ValueError:
        raise ApiError(422, "invalid_phone", "Enter a valid Iranian mobile number.")


def _ensure_student_group(user) -> None:
    group, _ = Group.objects.get_or_create(name=Role.STUDENT)
    user.groups.add(group)


@router.post("/otp/request", response={204: None}, auth=None)
def request_otp(request: HttpRequest, payload: PhoneIn):
    phone = _parse_phone(payload.phone)
    check_rate_limit("otp_phone_burst", phone, 3, 60)
    issue_otp(phone, payload.purpose, client_ip(request))
    return Status(204, None)


@router.post("/otp/verify", response=TokenOut, auth=None)
def confirm_otp(request: HttpRequest, payload: OtpVerifyIn):
    phone = _parse_phone(payload.phone)
    otp = verify_otp(phone, payload.purpose, payload.code, client_ip(request))
    try:
        with transaction.atomic():
            user, created = User.objects.get_or_create(
                phone=otp.phone,
                defaults={"is_active": True, "date_joined": timezone.now()},
            )
            if created:
                _ensure_student_group(user)
    except IntegrityError:
        user = User.objects.get(phone=otp.phone)
    if not user.is_active:
        raise ApiError(403, "account_disabled", "Account is disabled.")
    return _issued_response(tokens.create_token_pair(user, request=request))


@router.post("/login", response=TokenOut, auth=None)
def password_login(request: HttpRequest, payload: PasswordLoginIn):
    phone = _parse_phone(payload.phone)
    check_rate_limit("login_phone", phone, 10, 15 * 60)
    check_rate_limit("login_ip", client_ip(request) or "unknown", 30, 15 * 60)
    user = authenticate(request, phone=phone, password=payload.password)
    if user is None:
        raise ApiError(401, "invalid_credentials", "Phone or password is incorrect.")
    if not user.is_active:
        raise ApiError(403, "account_disabled", "Account is disabled.")
    return _issued_response(tokens.create_token_pair(user, request=request))


@router.post("/refresh", response=TokenOut, auth=None)
def refresh(request: HttpRequest):
    assert_csrf(request)
    value = request.COOKIES.get(settings.REFRESH_COOKIE_NAME, "")
    pair = tokens.rotate_refresh(value, request=request)
    return _issued_response(pair)


@router.post("/logout", response={204: None}, auth=None)
def logout(request: HttpRequest):
    assert_csrf(request)
    session = None
    value = request.COOKIES.get(settings.REFRESH_COOKIE_NAME, "")
    if value:
        try:
            payload = tokens.decode_token(value, expected_type="refresh")
            session = RefreshSession.objects.filter(jti=payload["jti"]).first()
        except ApiError:
            session = None
    tokens.revoke_session(session, reason="logout")
    response = Response({}, status=204)
    _clear_auth_cookies(response)
    return response


@router.get("/me", response=UserOut, auth=auth)
def me(request: HttpRequest):
    return user_out(require_authenticated(request.auth))


@router.patch("/me", response=UserOut, auth=auth)
def update_me(request: HttpRequest, payload: ProfileUpdateIn):
    user = require_authenticated(request.auth)
    assert_csrf(request)
    profile, _ = Profile.objects.get_or_create(user=user)
    data = payload.model_dump(exclude_unset=True)
    if "handle" in data and data["handle"]:
        clash = Profile.objects.filter(handle=data["handle"]).exclude(pk=profile.pk).exists()
        if clash:
            raise ApiError(409, "handle_taken", "This handle is already taken.")
    for field in ("display_name", "handle", "bio", "theme"):
        if field in data and data[field] is not None:
            setattr(profile, field, data[field])
    profile.save()
    return user_out(user)


@router.post("/password", response={204: None}, auth=auth)
def set_password(request: HttpRequest, payload: PasswordSetIn):
    user = require_authenticated(request.auth)
    assert_csrf(request)
    if user.has_usable_password():
        if not payload.current_password or not user.check_password(payload.current_password):
            raise ApiError(400, "wrong_password", "Current password is incorrect.")
    try:
        validate_password(payload.new_password, user=user)
    except Exception as exc:
        messages = getattr(exc, "messages", [str(exc)])
        raise ApiError(422, "weak_password", messages[0], messages)
    user.set_password(payload.new_password)
    user.save(update_fields=["password", "updated_at"])
    tokens.revoke_all_for_user(user, reason="password_changed")
    return Status(204, None)


@router.get("/sessions", response=list[SessionOut], auth=auth)
def list_sessions(request: HttpRequest):
    user = require_authenticated(request.auth)
    current_jti = request.COOKIES.get(settings.REFRESH_COOKIE_NAME, "")
    current = None
    if current_jti:
        try:
            current = tokens.decode_token(current_jti, expected_type="refresh")["jti"]
        except ApiError:
            current = None
    rows = RefreshSession.objects.filter(
        user=user, revoked_at__isnull=True, expires_at__gt=timezone.now()
    ).order_by("-created_at")[:50]
    return [
        SessionOut(
            id=str(row.jti),
            created_at=row.created_at,
            last_used_at=row.last_used_at,
            expires_at=row.expires_at,
            user_agent=row.user_agent,
            current=str(row.jti) == current,
        )
        for row in rows
    ]


@router.delete("/sessions/{session_id}", response={204: None}, auth=auth)
def revoke_session_endpoint(request: HttpRequest, session_id: str):
    user = require_authenticated(request.auth)
    assert_csrf(request)
    row = RefreshSession.objects.filter(user=user, jti=session_id, revoked_at__isnull=True).first()
    if row is None:
        raise ApiError(404, "not_found", "Session not found.")
    tokens.revoke_session(row, reason="user_revoked")
    return Status(204, None)
