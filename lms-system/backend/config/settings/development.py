"""
Development settings for LMS System.

This file contains settings specific to the development environment.
"""

from .base import *  # noqa: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Development-specific apps
INSTALLED_APPS += [  # noqa: F405
    'debug_toolbar',
]

# Development-specific middleware
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa: F405

INTERNAL_IPS = [
    '127.0.0.1',
    '10.0.2.2',
]

# CORS for development
CORS_ALLOW_ALL_ORIGINS = True

# CSRF for development
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000',
]

# Use SQLite for quick local testing (optional)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable rate limiting in development
RATELIMIT_ENABLE = False

# Debug toolbar settings
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}

# Static files
STATIC_URL = '/static/'

# Logging for development
LOGGING['loggers']['django']['level'] = 'DEBUG'  # noqa: F405
LOGGING['loggers']['lms']['level'] = 'DEBUG'  # noqa: F405

# Simplified password validation for development
AUTH_PASSWORD_VALIDATORS = []  # noqa: F405

# Cache for development (local memory)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}