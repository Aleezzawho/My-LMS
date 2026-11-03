"""Local development settings."""

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
AUTH_COOKIE_SECURE = False
TRUST_PROXY_HEADERS = False

INTERNAL_IPS = ["127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
LOG_LEVEL = "DEBUG"
LOGGING["root"]["level"] = LOG_LEVEL  # noqa: F405
