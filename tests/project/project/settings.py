from __future__ import annotations

from os.path import join
from pathlib import Path
from typing import Any

from django.core.handlers.asgi import ASGIRequest
from django.core.handlers.wsgi import WSGIRequest

from adjango.tasks import send_emails_task
from adjango.utils.common import traceback_str

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-@!c2^-9o^q#&te$c(u(k$l$cm^17p6p9e7cp1v8hnkdzg)a4^w'
DEBUG = True
ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'app.User'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'adjango',
    'app'
]


def handling_function(fn_name: str, request: WSGIRequest | ASGIRequest, e: Exception, *args: Any,
                      **kwargs: Any) -> None:
    """
    Пример функции обработки исключений.

    @param fn_name: Имя функции, в которой произошло исключение.
    @param request: Объект запроса (WSGIRequest или ASGIRequest).
    @param e: Исключение, которое нужно обработать.
    @param args: Позиционные аргументы, переданные в функцию.
    @param kwargs: Именованные аргументы, переданные в функцию.

    @return: None

    @usage:
        _handling_function(fn_name, request, e)
    """
    import logging
    log = logging.getLogger('global')
    error_text = (f'ERROR in {fn_name}:\n'
                  f'{traceback_str(e)}\n'
                  f'{request.POST=}\n'
                  f'{request.GET=}\n'
                  f'{request.FILES=}\n'
                  f'{request.COOKIES=}\n'
                  f'{request.user=}\n'
                  f'{args=}\n'
                  f'{kwargs=}')
    log.error(error_text)
    if not DEBUG:
        send_emails_task.delay(
            subject='SERVER ERROR',
            emails=('admin@example.com', 'admin2@example.com',),
            template='admin/exception_report.html',
            context={'error': error_text}
        )


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
ADJANGO_BACKENDS_APPS = BASE_DIR / 'apps'
ADJANGO_FRONTEND_APPS = BASE_DIR.parent / 'frontend' / 'src' / 'apps'
ADJANGO_APPS_PREPATH = 'apps.'  # if apps in BASE_DIR/apps/app1,app2...
# ADJANGO_APPS_PREPATH = None # if in BASE_DIR/app1,app2...
ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION = handling_function
ADJANGO_CONTROLLERS_LOGGER_NAME = 'global'
ADJANGO_CONTROLLERS_LOGGING = True
ADJANGO_EMAIL_LOGGER_NAME = 'email'

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

WSGI_APPLICATION = 'project.wsgi.application'

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
