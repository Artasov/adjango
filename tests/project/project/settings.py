# project/settings.py
from __future__ import annotations

from os.path import join
from pathlib import Path
from typing import Any

def _dummy_handler(fn_name, request, e, *args, **kwargs):
    """Simple placeholder error handler for tests."""
    return None

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-@!c2^-9o^q#&te$c(u(k$l$cm^17p6p9e7cp1v8hnkdzg)a4^w'
DEBUG = True
ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'app.User'

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'app'
]

# Celery
REDIS_BROKER_URL = 'redis://localhost:6379/0'
timezone = 'Europe/Moscow'
broker_url = REDIS_BROKER_URL
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 86400 * 30}
result_backend = REDIS_BROKER_URL
accept_content = ['application/json']
task_serializer = 'json'
result_serializer = 'json'
task_default_queue = 'default'
broker_connection_retry_on_startup = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = True

# adjango settings
LOGIN_URL = '/login/'
ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION = _dummy_handler
ADJANGO_IP_LOGGER = 'global'
ADJANGO_IP_META_NAME = 'HTTP_X_FORWARDED_FOR'

# For copy_project manage.py command
COPY_PROJECT_CONFIGURATIONS = BASE_DIR / 'project' / 'copy_conf.py'

MIDDLEWARE = [
    'adjango.middleware.IPAddressMiddleware',  # add request.ip in views
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = None
ASGI_APPLICATION = 'project.asgi.application'
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
}}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
