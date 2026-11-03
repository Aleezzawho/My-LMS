from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404, HttpRequest, HttpResponse
from ninja import NinjaAPI
from ninja.errors import HttpError, ValidationError
from pydantic import ValidationError as PydanticValidationError

from django.core.cache import cache
from django.db import connection

from apps.accounts.auth import auth, optional_auth
from apps.common.errors import error_payload
from apps.rbac.models import Role

api = NinjaAPI(
    title="LMS API",
    version="1.0.0",
    urls_namespace="v1",
    description="Interactive LMS and automated judge platform.",
)


def _request_id(request: HttpRequest) -> str:
    return getattr(request, "request_id", "")


@api.exception_handler(HttpError)
def http_error_handler(request: HttpRequest, exc: HttpError):
    code = getattr(exc, "code", None) or {
        400: "bad_request",
        401: "unauthenticated",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        429: "rate_limited",
    }.get(exc.status_code, "error")
    return api.create_response(
        request,
        error_payload(code, str(exc.message), getattr(exc, "details", None), _request_id(request)),
        status=exc.status_code,
    )


@api.exception_handler(ValidationError)
def validation_error_handler(request: HttpRequest, exc: ValidationError):
    details = []
    for item in exc.errors:
        details.append({"loc": [str(p) for p in item.get("loc", [])], "message": item.get("msg", "")})
    return api.create_response(
        request,
        error_payload("validation_error", "Invalid request payload.", details, _request_id(request)),
        status=422,
    )


@api.exception_handler(PydanticValidationError)
def pydantic_error_handler(request: HttpRequest, exc: PydanticValidationError):
    return api.create_response(
        request,
        error_payload(
            "validation_error",
            "Invalid request payload.",
            [{"loc": [str(p) for p in e["loc"]], "message": e["msg"]} for e in exc.errors()],
            _request_id(request),
        ),
        status=422,
    )


@api.exception_handler(DjangoValidationError)
def django_validation_error_handler(request: HttpRequest, exc: DjangoValidationError):
    message = exc.messages[0] if getattr(exc, "messages", None) else str(exc)
    return api.create_response(
        request,
        error_payload("validation_error", message, None, _request_id(request)),
        status=422,
    )


@api.exception_handler(Http404)
def not_found_handler(request: HttpRequest, exc: Http404):
    return api.create_response(
        request,
        error_payload("not_found", "Resource not found.", None, _request_id(request)),
        status=404,
    )


@api.exception_handler(Exception)
def unhandled_exception_handler(request: HttpRequest, exc: Exception):
    import logging

    logging.getLogger("api").exception("unhandled error path=%s", request.path)
    return api.create_response(
        request,
        error_payload("internal_error", "Something went wrong.", None, _request_id(request)),
        status=500,
    )


def attach(request, response: HttpResponse) -> HttpResponse:
    response["Cache-Control"] = "no-store"
    return response


def install_roles() -> dict[str, str]:
    from django.contrib.auth.models import Group

    groups = {}
    for role in Role.values:
        group, _ = Group.objects.get_or_create(name=role)
        groups[role] = group.name
    return groups


api.add_router("/auth", "apps.accounts.api.router")
api.add_router("/admin/rbac", "apps.rbac.api.router")


@api.get("/health", auth=None, tags=["ops"])
def health(request: HttpRequest):
    """Liveness plus dependency probe used by Traefik and the compose healthcheck."""
    checks = {"db": False, "cache": False}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks["db"] = True
    except Exception:
        pass
    try:
        cache.set("health:probe", 1, timeout=5)
        checks["cache"] = cache.get("health:probe") == 1
    except Exception:
        pass
    healthy = all(checks.values())
    return api.create_response(
        request,
        {"status": "ok" if healthy else "degraded", "checks": checks, "version": api.version},
        status=200 if healthy else 503,
    )
