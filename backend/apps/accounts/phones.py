import re

IRAN_MOBILE_RE = re.compile(r"^(?:\+98|0098|98|0)?(9\d{9})$")


def normalize_phone(raw: str) -> str:
    """Normalize Iranian mobile numbers to E.164 (`+98912...`).

    Raises ValueError for anything that is not a plausible Iranian mobile.
    """
    if not isinstance(raw, str):
        raise ValueError("phone must be a string")
    candidate = re.sub(r"[\s\-()]", "", raw)
    if candidate.startswith("00"):
        candidate = "+" + candidate[2:]
    match = IRAN_MOBILE_RE.match(candidate)
    if not match:
        raise ValueError("invalid Iranian mobile number")
    return "+98" + match.group(1)


def mask_phone(phone: str) -> str:
    return f"{phone[:4]}***{phone[-4:]}" if len(phone) >= 8 else "***"
