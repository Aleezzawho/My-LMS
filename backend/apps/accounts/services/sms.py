"""SMS provider adapters. One interface, swappable implementation."""

import json
import logging
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from django.conf import settings

logger = logging.getLogger(__name__)

KAVENEGAR_VERIFY_URL = "https://api.kavenegar.com/v1/{key}/verify/lookup.json"


class SmsError(Exception):
    """Raised when the provider definitively rejects a message."""


class SmsProvider(Protocol):
    def send_otp(self, phone: str, code: str) -> str:
        """Send a one-time code. Returns a provider reference for auditing."""


@dataclass
class ConsoleSmsProvider:
    """Development provider: writes the message to the log instead of the network."""

    def send_otp(self, phone: str, code: str) -> str:
        logger.info("sms.otp.console", extra={"phone": phone, "code": code})
        print(f"[sms] OTP for {phone}: {code}")
        return "console"


@dataclass
class MemorySmsProvider:
    """Test provider: records messages in a class-level outbox."""

    outbox: list = None

    def __post_init__(self):
        if MemorySmsProvider.outbox is None:
            MemorySmsProvider.outbox = []

    def send_otp(self, phone: str, code: str) -> str:
        MemorySmsProvider.outbox.append({"phone": phone, "code": code})
        return f"memory:{len(MemorySmsProvider.outbox)}"


@dataclass
class KavenegarSmsProvider:
    api_key: str
    template: str
    sender: str = ""
    timeout_seconds: int = 8

    def send_otp(self, phone: str, code: str) -> str:
        params = {
            "receptor": phone.lstrip("+") if phone.startswith("+98") else phone,
            "token": code,
            "template": self.template,
            "type": "sms",
        }
        if self.sender:
            params["sender"] = self.sender
        url = KAVENEGAR_VERIFY_URL.format(key=self.api_key)
        body = urllib.parse.urlencode(params).encode()
        request = urllib.request.Request(url, data=body, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode() or "{}")
        except Exception as exc:  # network, timeout, HTTP error
            logger.warning("sms.kavenegar.failed", extra={"phone": phone}, exc_info=exc)
            raise SmsError("sms provider unavailable") from exc
        if payload.get("return", {}).get("status") not in (200, None):
            raise SmsError(str(payload.get("return", {}).get("message", "provider rejected")))
        entries = payload.get("entries") or []
        return str(entries[0].get("messageid", "")) if entries else ""


_instance: SmsProvider | None = None


def get_sms_provider() -> SmsProvider:
    global _instance
    if _instance is not None:
        return _instance
    name = settings.SMS_PROVIDER
    if name == "kavenegar":
        if not settings.KAVENEGAR_API_KEY:
            raise SmsError("KAVENEGAR_API_KEY is not configured")
        _instance = KavenegarSmsProvider(
            api_key=settings.KAVENEGAR_API_KEY,
            template=settings.KAVENEGAR_TEMPLATE,
            sender=settings.KAVENEGAR_SENDER,
        )
    elif name == "memory":
        _instance = MemorySmsProvider()
    else:
        _instance = ConsoleSmsProvider()
    return _instance


def reset_sms_provider() -> None:
    global _instance
    _instance = None
