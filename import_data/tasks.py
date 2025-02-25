from movie_gen.celery import shared_task
from django.core.management import call_command

@shared_task
def import_tmdb_data_task():
    call_command('import_tmdb_data')
