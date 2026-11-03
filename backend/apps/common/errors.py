from typing import Any

from ninja.errors import HttpError


class ApiError(HttpError):
    """Consistent `{code, message, details}` error envelope."""

    def __init__(self, status_code: int, code: str, message: str, details: Any = None):
        super().__init__(status_code, message)
        self.code = code
        self.details = details


def error_payload(code: str, message: str, details: Any = None, request_id: str = "") -> dict:
    payload = {"code": code, "message": message, "details": details}
    if request_id:
        payload["request_id"] = request_id
    return payload
