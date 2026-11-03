"""Test settings: no external services required."""

from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "lms-tests",
    }
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
SMS_PROVIDER = "memory"
AUTH_COOKIE_SECURE = True
COOKIE_DOMAIN = None
TRUST_PROXY_HEADERS = False
SECRET_KEY = "test-secret-key-not-for-production"
LOGGING["root"]["level"] = "CRITICAL"  # noqa: F405
