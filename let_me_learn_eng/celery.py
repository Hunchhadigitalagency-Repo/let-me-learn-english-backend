import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "let_me_learn_eng.settings")

app = Celery("let_me_learn_eng")

# Read config from Django settings, using CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in installed apps
app.autodiscover_tasks()
