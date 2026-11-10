"""JWT access tokens plus rotating, revocable refresh sessions.

Threat model (short):
- Stolen refresh cookie: it is httpOnly + Secure + SameSite=Lax and bound to a family.
  Using a rotated (already used) token is treated as theft: the whole family is revoked.
- CSRF: refresh/logout accept the cookie, so they require a double-submit CSRF header
  whose value must match the non-httpOnly `lms_csrf` cookie.
- Replay of an access token after logout: access tokens are short-lived (15 min) and the
  refresh family is revoked, so the window is bounded by the TTL.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.common.errors import ApiError

from ..models import RefreshSession, User


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    access_expires_at: datetime
    refresh_session: RefreshSession


def _now() -> datetime:
    return timezone.now()


def issue_access_token(user: User, session: RefreshSession) -> tuple[str, datetime]:
    issued_at = _now()
    expires_at = issued_at + timedelta(seconds=settings.ACCESS_TOKEN_TTL_SECONDS)
    payload = {
        "sub": str(user.public_id),
        "typ": "access",
        "sid": str(session.jti),
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
        "iss": settings.JWT_ISSUER,
        "jti": uuid.uuid4().hex,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expires_at


def _new_session(user: User, request=None, parent: RefreshSession | None = None) -> RefreshSession:
    meta = {}
    if request is not None:
        meta["user_agent"] = request.META.get("HTTP_USER_AGENT", "")[:255]
        from apps.common.middleware import client_ip

        meta["ip"] = client_ip(request)
    return RefreshSession.objects.create(
        user=user,
        family=parent.family if parent else uuid.uuid4(),
        parent=parent,
        expires_at=_now() + timedelta(seconds=settings.REFRESH_TOKEN_TTL_SECONDS),
        **meta,
    )


def decode_token(token: str, expected_type: str = "access") -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            options={"require": ["exp", "iat", "sub", "typ"]},
        )
    except jwt.ExpiredSignatureError:
        raise ApiError(401, "token_expired", "Access token expired.") from None
    except jwt.InvalidTokenError:
        raise ApiError(401, "token_invalid", "Invalid token.") from None
    if payload.get("typ") != expected_type:
        raise ApiError(401, "token_invalid", "Invalid token type.")
    return payload


def create_token_pair(user: User, request=None) -> TokenPair:
    session = _new_session(user, request=request)
    access, expires_at = issue_access_token(user, session)
    return TokenPair(access_token=access, access_expires_at=expires_at, refresh_session=session)


def rotate_refresh(refresh_value: str, request=None) -> TokenPair:
    """Validate a refresh token, revoke it, and issue its successor.

    A token whose session is already revoked means two parties hold the same token;
    the entire family is revoked rather than handing out another pair.
    """
    if not refresh_value:
        raise ApiError(401, "refresh_missing", "No refresh session.")
    try:
        payload = jwt.decode(
            refresh_value,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            options={"require": ["exp", "iat", "sub", "typ"]},
        )
    except jwt.ExpiredSignatureError:
        raise ApiError(401, "refresh_expired", "Session expired. Sign in again.") from None
    except jwt.InvalidTokenError:
        raise ApiError(401, "refresh_invalid", "Invalid session.") from None
    if payload.get("typ") != "refresh":
        raise ApiError(401, "refresh_invalid", "Invalid session.")

    try:
        session = RefreshSession.objects.select_related("user").get(jti=payload["jti"])
    except (RefreshSession.DoesNotExist, ValueError):
        raise ApiError(401, "refresh_invalid", "Invalid session.") from None

    if session.revoked_at is not None:
        _revoke_family(session.family, reason="reuse_detected")
        raise ApiError(401, "refresh_reused", "Session revoked. Sign in again.")

    now = _now()
    if session.expires_at <= now:
        raise ApiError(401, "refresh_expired", "Session expired. Sign in again.")
    if not session.user.is_active:
        _revoke_family(session.family, reason="inactive_user")
        raise ApiError(401, "account_disabled", "Account is disabled.")

    with transaction.atomic():
        updated = RefreshSession.objects.filter(pk=session.pk, revoked_at__isnull=True).update(
            revoked_at=now, revoked_reason="rotated", last_used_at=now
        )
        if not updated:
            raise ApiError(401, "refresh_reused", "Session revoked. Sign in again.")
        child = _new_session(session.user, request=request, parent=session)
    access, expires_at = issue_access_token(session.user, child)
    return TokenPair(access_token=access, access_expires_at=expires_at, refresh_session=child)


def _revoke_family(family, reason: str) -> None:
    RefreshSession.objects.filter(family=family, revoked_at__isnull=True).update(
        revoked_at=_now(), revoked_reason=reason
    )


def revoke_session(session: RefreshSession | None, reason: str = "logout") -> None:
    if session is None:
        return
    _revoke_family(session.family, reason=reason)


def revoke_all_for_user(user: User, reason: str = "revoked") -> int:
    return RefreshSession.objects.filter(user=user, revoked_at__isnull=True).update(
        revoked_at=_now(), revoked_reason=reason
    )


def build_refresh_token(session: RefreshSession) -> str:
    issued_at = _now()
    payload = {
        "sub": str(session.user.public_id),
        "typ": "refresh",
        "jti": str(session.jti),
        "fid": str(session.family),
        "iat": int(issued_at.timestamp()),
        "exp": int(session.expires_at.timestamp()),
        "iss": settings.JWT_ISSUER,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
