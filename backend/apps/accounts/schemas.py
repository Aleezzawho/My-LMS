from datetime import datetime
from typing import Literal

from ninja import Schema
from pydantic import Field, field_validator


class PhoneIn(Schema):
    phone: str = Field(min_length=10, max_length=16)
    purpose: Literal["login", "reset"] = "login"


class OtpVerifyIn(Schema):
    phone: str = Field(min_length=10, max_length=16)
    code: str = Field(min_length=6, max_length=6)
    purpose: Literal["login", "reset"] = "login"


class PasswordLoginIn(Schema):
    phone: str = Field(min_length=10, max_length=16)
    password: str = Field(min_length=1, max_length=128)


class PasswordSetIn(Schema):
    current_password: str | None = Field(default=None, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class ProfileOut(Schema):
    display_name: str = ""
    handle: str | None = None
    bio: str = ""
    theme: str = "system"
    avatar_url: str | None = None


class UserOut(Schema):
    id: str
    phone: str
    email: str | None = None
    roles: list[str]
    profile: ProfileOut
    date_joined: datetime
    has_password: bool


class TokenOut(Schema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


class ProfileUpdateIn(Schema):
    display_name: str | None = Field(default=None, max_length=80)
    handle: str | None = Field(default=None, max_length=32)
    bio: str | None = Field(default=None, max_length=500)
    theme: Literal["system", "light", "dark"] | None = None

    @field_validator("handle")
    @classmethod
    def handle_format(cls, value: str | None):
        if value is None:
            return value
        import re

        if not re.fullmatch(r"[a-zA-Z0-9_]{3,32}", value):
            raise ValueError("handle must be 3-32 characters: letters, digits, underscore")
        return value.lower()


class SessionOut(Schema):
    id: str
    created_at: datetime
    last_used_at: datetime | None = None
    expires_at: datetime
    user_agent: str = ""
    current: bool = False


class MessageOut(Schema):
    code: str
    message: str
    details: dict | list | None = None
