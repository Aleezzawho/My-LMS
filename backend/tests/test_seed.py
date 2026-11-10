from io import StringIO

import pytest
from django.core.management import CommandError, call_command
from django.test import override_settings

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


@override_settings(DEBUG=True)
def test_seed_is_idempotent():
    call_command("seed_dev", stdout=StringIO())
    call_command("seed_dev", stdout=StringIO())
    assert User.objects.count() == 3
    admin = User.objects.get(phone="+989120000001")
    assert admin.is_superuser and admin.groups.filter(name="admin").exists()
    assert admin.profile.display_name


@override_settings(DEBUG=False)
def test_seed_refuses_in_production():
    with pytest.raises(CommandError):
        call_command("seed_dev")
