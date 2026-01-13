# from __future__ import absolute_import, unicode_literals
from celery import Celery
import platform
# from celery.schedules import crontab

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_gen.settings.dev')

app = Celery('movie_gen') # create an instance of Celery

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps. that the @shared_task decorator
app.autodiscover_tasks()

if platform.system() == 'Windows':
    print("Running on Windows system.")
    app.conf.task_always_eager = False
    app.conf.worker_concurrency = 1
    app.conf.broker_connection_retry_on_startup = True
else:
    print("Running on Linux system.")
    # app.conf.task_always_eager = False
    app.conf.worker_concurrency = 1  # Adjust based on your CPU cores
    app.conf.broker_connection_retry_on_startup = True