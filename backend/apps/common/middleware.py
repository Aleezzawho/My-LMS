import time
import uuid

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from .logging import request_id_var


def client_ip(request) -> str | None:
    """Resolve the caller IP, trusting X-Forwarded-For only behind our proxy."""
    if getattr(settings, "TRUST_PROXY_HEADERS", False):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            # Traefik appends the real peer; the left-most entry is client-controlled.
            candidate = forwarded.split(",")[-1].strip()
            if candidate:
                return candidate[:45]
        real_ip = request.META.get("HTTP_X_REAL_IP", "").strip()
        if real_ip:
            return real_ip[:45]
    return request.META.get("REMOTE_ADDR") or None


class RequestIdMiddleware(MiddlewareMixin):
    HEADER = "X-Request-ID"

    def process_request(self, request):
        incoming = request.headers.get(self.HEADER, "")
        request_id = incoming[:64] if incoming and incoming.isprintable() else uuid.uuid4().hex
        request.request_id = request_id
        request_id_var.set(request_id)
        request._start_time = time.monotonic()

    def process_response(self, request, response):
        response[self.HEADER] = getattr(request, "request_id", "")
        duration_ms = int((time.monotonic() - getattr(request, "_start_time", time.monotonic())) * 1000)
        response["Server-Timing"] = f"app;dur={duration_ms}"
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """A thin, always-on subset of headers; Traefik enforces the full CSP."""

    def process_response(self, request, response):
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("Referrer-Policy", "same-origin")
        if "Content-Security-Policy" not in response and not settings.DEBUG:
            response["Content-Security-Policy"] = (
                "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
            )
        return response
