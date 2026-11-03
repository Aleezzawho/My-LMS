import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client

from apps.accounts.services import sms

User = get_user_model()


@pytest.fixture(autouse=True)
def _clear_state():
    cache.clear()
    sms.reset_sms_provider()
    sms.MemorySmsProvider.outbox = []
    yield
    cache.clear()


@pytest.fixture
def api_client():
    return Client()


@pytest.fixture
def user(db):
    return User.objects.create_user(phone="09121234567", password="correct-horse-battery")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(phone="09129876543", password="correct-horse-battery")


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(phone="09120000000", password="correct-horse-battery")


@pytest.fixture
def sms_outbox():
    return sms.MemorySmsProvider.outbox


@pytest.fixture
def auth_client(api_client, user):
    response = api_client.post(
        "/api/v1/auth/login",
        {"phone": user.phone, "password": "correct-horse-battery"},
        content_type="application/json",
    )
    assert response.status_code == 200, response.content
    api_client.cookies["lms_csrf"] = response.cookies["lms_csrf"].value
    api_client.csrf_header = response.cookies["lms_csrf"].value
    api_client.user = user
    return api_client
