"""Celery application. Judge workers use the same app with dedicated queues."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("lms")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
