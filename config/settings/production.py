"""
Production settings for ibiza_comunidad project.

- Use mailgun to send emails
- Use Redis for cache

"""
from .base import *  # noqa

import logging
import os
import raven

print('Loading production')

RAVEN_CONFIG = {
    'dsn': env('DJANGO_SENTRY_DSN'),
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    # 'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
    'release': raven.fetch_git_sha(str(ROOT_DIR - 1)),
}

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG')
# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env('DJANGO_SECRET_KEY')

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ibiza_comunidad',
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': '',
        'PORT': '',
        'ATOMIC_REQUESTS': True,
    }
}

# This ensures that Django will be able to detect a secure connection
# properly on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# raven sentry client
# See https://docs.sentry.io/clients/python/integrations/django/
INSTALLED_APPS += ['raven.contrib.django.raven_compat', ]
RAVEN_MIDDLEWARE = ['raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware']
MIDDLEWARE = RAVEN_MIDDLEWARE + MIDDLEWARE


# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/en/dev/howto/deployment/checklist/#run-manage-py-check-deploy

# set this to 60 seconds and then to 518400 when you can prove it works
SECURE_HSTS_SECONDS = 518400
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    'DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    'DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Disabling the below settings, moght only be for SSL
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['ibizacomunidad.es', ])
# END SITE CONFIGURATION

INSTALLED_APPS += ['gunicorn', ]

# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND')
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL')
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default='[ibiza_comunidad]')
# EMAIL_HOST = env('DJANGO_EMAIL_HOST')
# EMAIL_PORT = env('DJANGO_EMAIL_PORT')
# EMAIL_HOST_USER = env('DJANGO_EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = env('DJANGO_EMAIL_HOST_PASSWORD')
# EMAIL_USE_TLS = env.bool('DJANGO_EMAIL_USE_TLS')

# CACHING
# ------------------------------------------------------------------------------

REDIS_LOCATION = '{0}/{1}'.format(env('REDIS_URL', default='redis://127.0.0.1:6379'), 0)
# Heroku URL does not pass the DB number, so we parse it in
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_LOCATION,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,  # mimics memcache behavior.
                                        # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
        }
    }
}

# LOGGING

# Add logger settings to base.py
LOGGING['root'] = {
    'level': 'WARNING',
    'handlers': ['sentry'],
}
LOGGING['handlers']['sentry'] = {
    'level': 'WARNING', # To capture more than ERROR, change to WARNING, INFO, etc.
    'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
}
# Write to log file
LOGGING['handlers']['file'] = {
    'level': 'INFO',
    'class': 'logging.FileHandler',
    'filename': '/home/mistalaba/logs/ibiza_comunidad_django.log',
    'formatter': 'verbose',
    'filters': ['require_debug_false'],
}

LOGGING['loggers']['django']['handlers'].append('file')

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
