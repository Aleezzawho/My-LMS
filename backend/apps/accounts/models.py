import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel, UUIDModel

from .phones import normalize_phone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _prepare(self, phone: str, email: str | None, **extra):
        if not phone:
            raise ValueError("phone is required")
        user = self.model(phone=normalize_phone(phone), email=self.normalize_email(email), **extra)
        return user

    def normalize_email(self, email: str | None) -> str | None:
        if not email:
            return None
        return email.strip().lower() or None

    def create_user(self, phone: str, password: str | None = None, **extra):
        user = self._prepare(phone, extra.pop("email", None), **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone: str, password: str, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_active", True)
        if extra["is_staff"] is not True or extra["is_superuser"] is not True:
            raise ValueError("superuser must have is_staff and is_superuser set")
        return self.create_user(phone, password, **extra)


class User(AbstractBaseUser, PermissionsMixin, UUIDModel):
    phone = models.CharField(
        max_length=16,
        unique=True,
        validators=[RegexValidator(r"^\+989\d{9}$", "Invalid Iranian mobile number")],
    )
    email = models.EmailField(unique=True, null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        db_table = "accounts_user"
        ordering = ["-date_joined"]

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = normalize_phone(self.phone)
        if self.email:
            self.email = self.email.strip().lower() or None
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.phone

    @property
    def display_label(self) -> str:
        profile = getattr(self, "profile", None)
        if profile and profile.display_name:
            return profile.display_name
        return self.phone


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=80, blank=True)
    handle = models.CharField(max_length=32, unique=True, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar_key = models.CharField(max_length=255, blank=True)
    theme = models.CharField(
        max_length=8,
        choices=[("system", "System"), ("light", "Light"), ("dark", "Dark")],
        default="system",
    )

    class Meta:
        db_table = "accounts_profile"

    def __str__(self) -> str:
        return f"Profile<{self.user_id}>"


class OtpPurpose(models.TextChoices):
    LOGIN = "login", "Login"
    RESET = "reset", "Password reset"


class OtpRequest(TimeStampedModel):
    phone = models.CharField(max_length=16, db_index=True)
    purpose = models.CharField(max_length=16, choices=OtpPurpose.choices, default=OtpPurpose.LOGIN)
    code_hash = models.CharField(max_length=255)
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=5)
    expires_at = models.DateTimeField()
    requested_ip = models.GenericIPAddressField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)
    delivery_ref = models.CharField(max_length=120, blank=True)

    class Meta:
        db_table = "accounts_otp_request"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["phone", "purpose", "created_at"])]

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_consumable(self) -> bool:
        return (
            self.consumed_at is None
            and not self.is_expired
            and self.attempts < self.max_attempts
        )


class RefreshSession(models.Model):
    """One node in a refresh-token family; rotation creates a child node."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="refresh_sessions")
    jti = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    family = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True, db_index=True)
    revoked_reason = models.CharField(max_length=32, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_refresh_session"
        indexes = [models.Index(fields=["user", "family"])]

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None and self.expires_at > timezone.now()
