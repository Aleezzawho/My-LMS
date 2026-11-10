"""Base settings shared by every environment."""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BASE_DIR.parent

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "insecure-dev-key-change-me"),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    DATABASE_URL=(str, "postgres://lms:lms@localhost:5432/lms"),
    REDIS_URL=(str, "redis://localhost:6379/0"),
    CELERY_BROKER_URL=(str, "amqp://lms:lms@localhost:5672//"),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:3000"]),
    CSRF_TRUSTED_ORIGINS=(list, []),
    TRUST_PROXY_HEADERS=(bool, False),
    SMS_PROVIDER=(str, "console"),
    KAVENEGAR_API_KEY=(str, ""),
    KAVENEGAR_SENDER=(str, ""),
    KAVENEGAR_TEMPLATE=(str, "lms-otp"),
    ACCESS_TOKEN_TTL_SECONDS=(int, 15 * 60),
    REFRESH_TOKEN_TTL_SECONDS=(int, 7 * 24 * 60 * 60),
    OTP_TTL_SECONDS=(int, 2 * 60),
    OTP_MAX_ATTEMPTS=(int, 5),
    OTP_RESEND_COOLDOWN_SECONDS=(int, 60),
    COOKIE_DOMAIN=(str, ""),
    AUTH_COOKIE_SECURE=(bool, False),
    LOG_LEVEL=(str, "INFO"),
)

env_file = REPO_ROOT / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "apps.common",
    "apps.accounts",
    "apps.rbac",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "apps.common.middleware.RequestIdMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.common.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = 60

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "KEY_PREFIX": "lms",
    }
}

AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
]
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / "locale"]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-request-id",
    "idempotency-key",
]
CORS_EXPOSE_HEADERS = ["x-request-id", "retry-after"]

# Domain settings
TRUST_PROXY_HEADERS = env("TRUST_PROXY_HEADERS")
SMS_PROVIDER = env("SMS_PROVIDER")
KAVENEGAR_API_KEY = env("KAVENEGAR_API_KEY")
KAVENEGAR_SENDER = env("KAVENEGAR_SENDER")
KAVENEGAR_TEMPLATE = env("KAVENEGAR_TEMPLATE")

ACCESS_TOKEN_TTL_SECONDS = env("ACCESS_TOKEN_TTL_SECONDS")
REFRESH_TOKEN_TTL_SECONDS = env("REFRESH_TOKEN_TTL_SECONDS")
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "lms"

OTP_TTL_SECONDS = env("OTP_TTL_SECONDS")
OTP_MAX_ATTEMPTS = env("OTP_MAX_ATTEMPTS")
OTP_RESEND_COOLDOWN_SECONDS = env("OTP_RESEND_COOLDOWN_SECONDS")

COOKIE_DOMAIN = env("COOKIE_DOMAIN") or None
AUTH_COOKIE_SECURE = env("AUTH_COOKIE_SECURE")
ACCESS_COOKIE_NAME = "lms_access"
REFRESH_COOKIE_NAME = "lms_refresh"
CSRF_COOKIE_NAME = "lms_csrf"
REFRESH_COOKIE_PATH = "/api/v1/auth"

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_QUEUES = {
    "judge.contest": {"exchange": "judge", "routing_key": "judge.contest"},
    "judge.practice": {"exchange": "judge", "routing_key": "judge.practice"},
    "judge.custom_run": {"exchange": "judge", "routing_key": "judge.custom_run"},
    "judge.rejudge": {"exchange": "judge", "routing_key": "judge.rejudge"},
    "default": {"exchange": "default", "routing_key": "default"},
}
CELERY_TASK_TIME_LIMIT = 10 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 9 * 60

LOG_LEVEL = env("LOG_LEVEL")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": "apps.common.logging.JsonFormatter"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}
