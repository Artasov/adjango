# conf.py
from django.conf import settings


def get_setting(name, default=None, required=False):
    value = getattr(settings, name, None)
    if value is None:
        if required:
            if default is not None:
                return default
            raise ValueError(f'Missing required django setting: {name}')
        return default
    return value


ADJANGO_BACKENDS_APPS = get_setting('ADJANGO_BACKENDS_APPS', settings.BASE_DIR)
ADJANGO_FRONTEND_APPS = get_setting('ADJANGO_FRONTEND_APPS', settings.BASE_DIR)
ADJANGO_APPS_PREPATH = get_setting('ADJANGO_APPS_PREPATH')
ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION = get_setting(
    'ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION',
)
ADJANGO_CONTROLLERS_LOGGER_NAME = get_setting('ADJANGO_CONTROLLERS_LOGGER_NAME', 'global')
ADJANGO_CONTROLLERS_LOGGING = get_setting(
    'ADJANGO_CONTROLLERS_LOGGING',
)
ADJANGO_EMAIL_LOGGER_NAME = get_setting('ADJANGO_EMAIL_LOGGER_NAME', 'email')
ADJANGO_IP_LOGGER = get_setting('ADJANGO_IP_LOGGER')
ADJANGO_IP_META_NAME = get_setting('ADJANGO_IP_META_NAME')
MEDIA_SUBSTITUTION_URL = get_setting('MEDIA_SUBSTITUTION_URL')
ADJANGO_BASE_LOGGER = get_setting('ADJANGO_BASE_LOGGER')
