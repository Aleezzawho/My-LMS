"""Request authentication for Django Ninja.

Browsers use the httpOnly access cookie; API clients may send a bearer token.
"""

from django.conf import settings
from ninja.security import HttpBearer

from apps.common.errors import ApiError

from .models import RefreshSession, User
from .services.tokens import decode_token


def user_from_access_token(token: str) -> User:
    payload = decode_token(token, expected_type="access")
    session = (
        RefreshSession.objects.select_related("user")
        .filter(jti=payload.get("sid"), revoked_at__isnull=True)
        .first()
    )
    if session is None:
        raise ApiError(401, "session_revoked", "Session is no longer valid.")
    if not session.user.is_active:
        raise ApiError(401, "account_disabled", "Account is disabled.")
    return session.user


class CookieOrBearerAuth(HttpBearer):
    def authenticate(self, request, token):
        return user_from_access_token(token)

    def __call__(self, request):
        token = request.COOKIES.get(settings.ACCESS_COOKIE_NAME, "")
        if token:
            try:
                return user_from_access_token(token)
            except ApiError:
                return None
        return super().__call__(request)


class OptionalAuth(CookieOrBearerAuth):
    def __call__(self, request):
        return super().__call__(request)


auth = CookieOrBearerAuth()
optional_auth = OptionalAuth()
