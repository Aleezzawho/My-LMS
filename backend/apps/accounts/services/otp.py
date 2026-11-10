"""SMS OTP issuance and verification.

Threat model (short):
- Code guessing: 6 digits, 2-minute TTL, 5 attempts per code, code consumed on success.
- SMS bombing: per-phone cooldown plus per-phone and per-IP hourly budgets, all in Redis.
- DB leak: only a hash of the code is stored; plaintext never touches the database or logs
  outside the (dev-only) console provider.
- Replay: the row is marked consumed before tokens are issued; used rows can never pass again.
- Enumeration: send always answers 204 regardless of whether the phone has an account.
"""

import logging
import secrets

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.utils import timezone

from apps.common.errors import ApiError
from apps.common.ratelimit import check_rate_limit

from ..models import OtpPurpose, OtpRequest
from .sms import SmsError, get_sms_provider

logger = logging.getLogger(__name__)

SEND_PER_PHONE = (5, 15 * 60)
SEND_PER_IP = (20, 60 * 60)
VERIFY_PER_PHONE = (15, 10 * 60)
VERIFY_PER_IP = (60, 10 * 60)


def _cooldown_key(phone: str, purpose: str) -> str:
    return f"otp:cooldown:{purpose}:{phone}"


def issue_otp(phone: str, purpose: str, request_ip: str | None) -> None:
    from django.core.cache import cache

    if purpose not in OtpPurpose.values:
        raise ApiError(400, "invalid_purpose", "Unknown OTP purpose.")

    check_rate_limit("otp_send_phone", phone, *SEND_PER_PHONE)
    if request_ip:
        check_rate_limit("otp_send_ip", request_ip, *SEND_PER_IP)

    key = _cooldown_key(phone, purpose)
    if not cache.add(key, 1, timeout=settings.OTP_RESEND_COOLDOWN_SECONDS):
        raise ApiError(429, "otp_too_soon", "Wait before requesting another code.")

    code = f"{secrets.randbelow(1_000_000):06d}"
    now = timezone.now()
    with transaction.atomic():
        OtpRequest.objects.filter(phone=phone, purpose=purpose, consumed_at__isnull=True).update(
            consumed_at=now
        )
        otp = OtpRequest.objects.create(
            phone=phone,
            purpose=purpose,
            code_hash=make_password(code),
            expires_at=now + timezone.timedelta(seconds=settings.OTP_TTL_SECONDS),
            max_attempts=settings.OTP_MAX_ATTEMPTS,
            requested_ip=request_ip,
        )

    try:
        reference = get_sms_provider().send_otp(phone, code)
    except SmsError as exc:
        otp.consumed_at = timezone.now()
        otp.save(update_fields=["consumed_at"])
        cache.delete(key)
        raise ApiError(
            503, "sms_unavailable", "Could not send the code. Try again shortly."
        ) from exc

    if reference:
        OtpRequest.objects.filter(pk=otp.pk).update(delivery_ref=reference[:120])


def verify_otp(phone: str, purpose: str, code: str, request_ip: str | None) -> OtpRequest:
    """Verify and consume a code. Raises ApiError on any failure path."""
    if not code or not code.isdigit() or len(code) != 6:
        raise ApiError(400, "invalid_code_format", "The code must be 6 digits.")

    check_rate_limit("otp_verify_phone", phone, *VERIFY_PER_PHONE)
    if request_ip:
        check_rate_limit("otp_verify_ip", request_ip, *VERIFY_PER_IP)

    failure: ApiError | None = None
    with transaction.atomic():
        otp = (
            OtpRequest.objects.select_for_update()
            .filter(phone=phone, purpose=purpose, consumed_at__isnull=True)
            .order_by("-created_at")
            .first()
        )
        if otp is None:
            recently_locked = (
                OtpRequest.objects.filter(
                    phone=phone,
                    purpose=purpose,
                    attempts__gte=settings.OTP_MAX_ATTEMPTS,
                    created_at__gte=timezone.now()
                    - timezone.timedelta(seconds=settings.OTP_TTL_SECONDS),
                )
                .order_by("-created_at")
                .exists()
            )
            failure = (
                ApiError(429, "otp_locked", "Too many attempts. Request a new code.")
                if recently_locked
                else ApiError(400, "otp_invalid", "The code is incorrect or has expired.")
            )

        if otp is not None:
            now = timezone.now()
            if now >= otp.expires_at:
                otp.consumed_at = now
                otp.save(update_fields=["consumed_at"])
                failure = ApiError(400, "otp_expired", "The code is incorrect or has expired.")
            elif otp.attempts >= otp.max_attempts:
                otp.consumed_at = now
                otp.save(update_fields=["consumed_at"])
                failure = ApiError(429, "otp_locked", "Too many attempts. Request a new code.")
            elif not check_password(code, otp.code_hash):
                # Persist the failed attempt; raising inside this block would roll it back.
                otp.attempts += 1
                if otp.attempts >= otp.max_attempts:
                    otp.consumed_at = now
                    otp.save(update_fields=["attempts", "consumed_at"])
                    failure = ApiError(429, "otp_locked", "Too many attempts. Request a new code.")
                else:
                    otp.save(update_fields=["attempts"])
                    failure = ApiError(400, "otp_invalid", "The code is incorrect or has expired.")
            else:
                otp.consumed_at = now
                otp.save(update_fields=["consumed_at"])

    if failure is not None:
        raise failure
    assert otp is not None
    return otp
