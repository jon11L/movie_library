from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command

# from datetime import datetime

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3)
def import_tmdb_data_task(self):
    logger.info('Starting import_tmdb_data_task')
    try:
        # Log more details about the environment
        import os
        import sys
        logger.info('Working directory: %s', os.getcwd())
        logger.info('Python path: %s', sys.path)
        logger.info('Environment variables: %s', dict(os.environ))
        
        logger.info('Calling management command import_tmdb_data')
        call_command('import_tmdb_data')
        logger.info('Management command import_tmdb_data completed successfully')
        return True
    except Exception as exc:
        logger.error('Task failed: %s', exc, exc_info=True)  # Include traceback
        raise self.retry(exc=exc, countdown=60)

# @shared_task
# def debug_task():
#     with open('celery_debug.txt', 'a') as f:
#         f.write(f"Task ran at: {datetime.now()}\n")
#     return "Debug task completed successfully"

# testing 
# @shared_task
# def test_task():
#     logger.info('Running test task')
#     return "Task completed successfully!"