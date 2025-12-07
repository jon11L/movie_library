"""
Production settings - Use this on AWS
NEVER run with DEBUG=True in production
"""

from .base import *
import os


# SECURITY - CRITICAL
DEBUG = False  # NEVER True in production

ALLOWED_HOSTS = [] # place domain names or IP addresses here, e.g. when deploying to production
print("using prod setting")

# Security for Https
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# SECURE_HSTS_SECONDS = 3600    

SECURE_BROWSER_XSS_FILTER = True # against Attack: Cross-Site Scripting (XSS)
# Protect against suspicious upload /eg. fake .jpg that are actual javascript
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY' # Prevents from being embedded in iframes




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