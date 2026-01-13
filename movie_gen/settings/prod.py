"""
Production settings - Use this on AWS
NEVER run with DEBUG=True in production
"""

from .base import *
import os

# SECURITY - CRITICAL
DEBUG = False  # NEVER True in production

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

ALLOWED_HOSTS = [
    os.environ.get('ALLOWED_HOST', ''),
    '3.66.157.212',  # Your EC2 public IP
    'localhost',
    '127.0.0.1',
] # place domain names or IP addresses here, e.g. when deploying to production
print("**using production setting**")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ['RDS_DB_NAME'],
        "USER": os.environ['RDS_USERNAME'],
        "PASSWORD": os.environ['RDS_PASSWORD'],
        "HOST": os.environ['RDS_HOSTNAME'],
        "PORT": os.environ.get('RDS_PORT', '5432'),
    }
}


# AWS S3  -- in process
# AWS setting 
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME_STATIC = os.environ['AWS_STORAGE_BUCKET_NAME_STATIC']
AWS_STORAGE_BUCKET_NAME_MEDIA = os.environ['AWS_STORAGE_BUCKET_NAME_MEDIA']
AWS_S3_REGION_NAME = 'eu-central-1'  # Frankfurt

AWS_S3_CUSTOM_DOMAIN_STATIC = f'{AWS_STORAGE_BUCKET_NAME_STATIC}.s3.amazonaws.com'
AWS_S3_CUSTOM_DOMAIN_MEDIA = f'{AWS_STORAGE_BUCKET_NAME_MEDIA}.s3.amazonaws.com'

AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'} # cache for 1 day
AWS_DEFAULT_ACL = None

# ============ Static file configuration to S3   =============
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN_STATIC}/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] # Django looks here // Only work on DEV server

# Media  on S3
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN_MEDIA}/media/'

# ==== Static files - Before served with EC2 (now S3) ==========
# STATIC_URL = '/static/' # 


# -- Media files --
# MEDIA_URL = '/media/'

# Where collectstatic will store static files. //Temp remove when S3 set  up
STATIC_ROOT = '/var/www/html/staticfiles'
MEDIA_ROOT = '/var/www/html/media'

STORAGES = {
    "default": {  # For media files (user uploads)
        "BACKEND": "movie_gen.storage_backends.MediaStorage",
    },
    "staticfiles": {  # For static files (CSS, JS, etc..)
        "BACKEND": "movie_gen.storage_backends.StaticStorage",
    },
}


# Security for Https
SECURE_SSL_REDIRECT = False # Set True when  have HTTPS
SESSION_COOKIE_SECURE = False # Set True when  have HTTPS
CSRF_COOKIE_SECURE = False # Set True when  have HTTPS

# HSTS settings  --> broswer request should not connect to an HTTP/insecure connection
# SECURE_HSTS_SECONDS = 3600   # 1h, switch to 31536000 - 1year when running correctly 
# SECURE_HSTS_PRELOAD = True 
# SECURE_HSTS_INCLUDE_SUBDOMAINS 

SECURE_BROWSER_XSS_FILTER = True # against Attack: Cross-Site Scripting (XSS)
# Protect against suspicious upload /eg. fake .jpg that are actual javascript
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY' # Prevents from being embedded in iframes


# =========================== Celery + REDIS feature =============================
CELERY_BROKER_URL = f'redis://localhost:6379/1' # Use Redis as the message broker
CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'  # Use Redis as the result backend


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


# ============ Will implement the logging later ============================0
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'ERROR',
#             'class': 'logging.FileHandler',
#             'filename': '/var/log/django/error.log',  # Write to file
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'ERROR',  # Only log errors and critical
#             'propagate': True,
#         },
#     },
# }



# debug At the END of settings/prod.py
print("=" * 50)
print("DEBUG: Django Storage Configuration")
print(f"STORAGES = {STORAGES}")
print(f"STATIC_ROOT = {STATIC_ROOT}")
print(f"AWS_STORAGE_BUCKET_NAME_STATIC = {AWS_STORAGE_BUCKET_NAME_STATIC}")
print("=" * 50)

