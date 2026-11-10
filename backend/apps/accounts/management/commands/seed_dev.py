"""Create roles and demo users for local development.

Catalog, problems, and contest seed data are added by later phases as those
apps land; this command stays idempotent so it can be re-run at any time.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError

from apps.rbac.models import Role

DEMO_PASSWORD = "demo-pass-1234"
DEMO_USERS = [
    ("09120000001", "مدیر نمونه", [Role.ADMIN], True),
    ("09120000002", "نویسنده نمونه", [Role.CREATOR], False),
    ("09120000003", "دانشجوی نمونه", [Role.STUDENT], False),
]


class Command(BaseCommand):
    help = "Seed roles and demo users (development only)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_dev refuses to run with DEBUG=False.")

        groups = {role: Group.objects.get_or_create(name=role)[0] for role in Role.values}
        user_model = get_user_model()

        for phone, display_name, roles, is_admin in DEMO_USERS:
            user = user_model.objects.filter(phone=f"+98{phone[1:]}").first()
            if user is None:
                user = user_model.objects.create_user(
                    phone=phone, password=DEMO_PASSWORD, is_staff=is_admin, is_superuser=is_admin
                )
            user.groups.add(*(groups[role] for role in roles))
            user.profile.display_name = display_name
            user.profile.save(update_fields=["display_name", "updated_at"])
            self.stdout.write(f"  {user.phone}  roles={','.join(roles)}")

        self.stdout.write(self.style.SUCCESS(f"Seeded. Demo password: {DEMO_PASSWORD}"))
