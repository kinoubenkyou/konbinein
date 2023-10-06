import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "konbinein.settings")

app = Celery("konbinein")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.broker_url = "redis://localhost:6379/0"

app.conf.result_backend = "redis://localhost:6379/0"
