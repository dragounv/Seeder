from .base import *

SECRET_KEY = 'sdfvsdfvsdfvsdfv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
THUMBNAIL_DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
# since we use special PostgresSQL fields we cannot simply use any db.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'postgres',
    },
    'legacy_seeder': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'legacy_db',
        'USER': 'legacy',
        'PASSWORD': 'legacy',
        'HOST': 'mysql',
    }
}


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://elastic:9200/',
        'INDEX_NAME': 'haystack',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'memcached:11211',
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
LEGACY_DB_CONNECTED = True

MANET_URL = 'http://manet:8891/'
