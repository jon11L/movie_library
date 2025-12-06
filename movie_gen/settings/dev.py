"""
Development settings - Use this locally
Run with: python manage.py runserver --settings=movie_gen.settings.dev
"""
from .base import *
import os
from dotenv import load_dotenv

load_dotenv()


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1'] # place domain names or IP addresses here, e.g. when deploying to production

# Add devtools only in development
INSTALLED_APPS += ['devtools']


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] # Only work on DEV server
# ===============
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Where collectstatic puts files for Production.
# ==========================

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'



# ============================ LOGGING =================================
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#         },
#         # "file": {
#         #     "level": "DEBUG",
#         #     "class": "logging.FileHandler",
#         #     "filename": "/path/to/django/debug.log",
#         # },
#     },
#     "root": {
#         "handlers": ["console"],
#         "level": "WARNING",
#     },
# }



# Detect operating system
CURRENT_OS = platform.system()
print(f"Detected OS: {CURRENT_OS}")

# ============== Configuration  for Celery and RabbitMQ/Redis ====================
if CURRENT_OS == 'Windows':
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PW = os.getenv('RABBITMQ_PASSWORD', 'guest')

    CELERY_BROKER_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PW}@localhost:5672//'  # Use RabbitMQ as the message broker // for windows use.
    CELERY_RESULT_BACKEND = 'rpc://'  # Use RabbitMQ as the result backend
    # print("Using **RabbitMQ** as the message broker and result backend for Windows.") # debug log

    CELERY_BROKER_TRANSPORT_OPTIONS = {
        'visibility_timeout': 3600,
        # 'heartbeat': 0,  
        # 'connection_timeout': 5000
    }

elif CURRENT_OS == 'Linux':
    CELERY_BROKER_URL = f'redis://localhost:6379/1' # Use Redis as the message broker // for Linux use. 
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'  # Use Redis as the result backend // for Linux use.
    # print("Using **Redis** as the message broker and result backend for Linux.") # debug log

    # Redis-specific broker options
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        'visibility_timeout': 3600,
        'retry_on_timeout': True,
        'connection_pool_kwargs': {
            'max_connections': 20,
            'retry_on_timeout': True,
        },
    }

else: # Fallback for other systems (macOS, etc.) - use Redis
    CELERY_BROKER_URL = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'
    print(f"Using Redis broker for {CURRENT_OS} (fallback)") # debug log
    
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        'visibility_timeout': 3600,
        'retry_on_timeout': True,
    }

# CELERY_RESULT_BACKEND = 'rpc://'  # Use RabbitMQ as the result backend
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BEAT_MAX_LOOP_INTERVAL = 60 # look for change in DB every 60 seconds

# heartbeat 0 should fix the issue with ''  Couldn't ack 1, reason:ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None) ''
CELERY_BROKER_HEARTBEAT = 0
CELERY_TASK_ACKS_LATE = True  # Ensures tasks are acknowledged only when completed
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Berlin'

CELERY_WORKER_PREFETCH_MULTIPLIER = 1 # Set to 1 to ensure tasks are processed one at a time