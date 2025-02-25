from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_gen.settings')

app = Celery('movie_gen') # create an instance of Celery

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Message broker part for Celery to send messages.
app.conf.beat_schedule = {
    'import-tmdb-data-every-day': {
        'task': 'import_data.tasks.import_tmdb_data_task',
        'schedule': crontab(minute=15, hour=17),  # Daily at 2pm
    },
}
app.conf.timezone = 'UTC'