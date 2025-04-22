from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command

# from datetime import datetime

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3)
def task_import_movies(self):
    try:
        logger.info('Invoking command Task: *import new movies* from TDMB database')        
        # Log more details about the environment
        # import os
        # import sys
        # logger.info('Working directory: %s', os.getcwd())
        # logger.info('Python path: %s', sys.path) 
        # logger.info('Environment variables: %s', dict(os.environ))
        call_command('import_tmdb_movies')
        logger.info('Management command Task: *import new movies* completed successfully')
        return True
    except Exception as exc:
        logger.error('Task failed: %s', exc, exc_info=True)  # Include traceback
        retry_countdown = self.request.retries * 30
        logger.info(f'Retrying task in {retry_countdown} seconds...') 
        raise self.retry(exc=exc, countdown=retry_countdown)


@shared_task(bind=True, max_retries=3)
def task_update_movies(self):
    """
    Periodic Celery task to update movies that have been modified in TMDB.
    """
    try:
        logger.info('Invoking command Task: *update movies* from TDMB database')        
        call_command('update_tmdb_movies')
        logger.info('Management command Task: *update movies* completed successfully')
        return True
    except Exception as e:
        logger.error('Task failed: %s', e, exc_info=True)  # Include traceback
        retry_countdown = self.request.retries * 30
        logger.info(f'Retrying task in {retry_countdown} seconds...')
        raise self.retry(exc=e, countdown=retry_countdown)


@shared_task(bind=True, max_retries=3)
def task_import_series(self):
    """
    Periodic Celery task to fetch new series in TMDB.
    """
    try:
        logger.info('Invoking command Task: *import new series* from TMDB database')        
        call_command('import_tmdb_series')
        logger.info('Management command Task: *import new series* completed successfully')
        return True
    
    except Exception as exc:
        logger.error('Task failed: %s', exc, exc_info=True)  # Include traceback
        retry_countdown = self.request.retries * 30
        logger.info(f'Retrying task in {retry_countdown} seconds...') 
        raise self.retry(exc=exc, countdown=retry_countdown)


@shared_task(bind=True, max_retries=3)
def task_update_series(self):
    """
    Periodic Celery task to update series that have been modified in TMDB.
    """
    try:
        logger.info('Invoking command Task: *update series* from TDMB database')        
        call_command('update_tmdb_series')
        logger.info('Management command import_tmdb_data completed successfully')
        return True
    
    except Exception as exc:
        logger.error('Task failed: %s', exc, exc_info=True)  # Include traceback
        retry_countdown = self.request.retries * 30
        logger.info(f'Retrying task in {retry_countdown} seconds...') 
        raise self.retry(exc=exc, countdown=retry_countdown)


# just to correct the production field in movies // issues with creation of nested list instead of list
# @shared_task(bind=True, max_retries=3)
# def task_correct_movies(self):
#     """
#     Periodic Celery task to update series that have been modified in TMDB.
#     """
#     try:
#         logger.info('Invoking command Task: correct movies(production)')        
#         call_command('correct_production_movies')
#         logger.info('Management command import_tmdb_data completed successfully')
#         return True
    
#     except Exception as exc:
#         logger.error('Task failed: %s', exc, exc_info=True)  # Include traceback
#         retry_countdown = self.request.retries * 30
#         logger.info(f'Retrying task in {retry_countdown} seconds...') 
#         raise self.retry(exc=exc, countdown=retry_countdown)


# testing 
# @shared_task
# def test_task():
#     logger.info('Running test task')
#     return "Task completed successfully!"