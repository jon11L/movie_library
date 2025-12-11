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

print("using dev setting")

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



# =============== Static files (CSS, JavaScript, Images) ========================
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] # Only work on DEV server
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Where collectstatic puts files for Production.

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'



# ============================ LOGGING =================================
# ============ Will implement the logging later ============================0

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

