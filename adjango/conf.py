# conf.py
from django.conf import settings


def get_setting(setting_name, default):
    return getattr(settings, setting_name, default)


ADJANGO_BACKENDS_APPS = get_setting('ADJANGO_BACKENDS_APPS', settings.BASE_DIR)
ADJANGO_FRONTEND_APPS = get_setting('ADJANGO_FRONTEND_APPS', settings.BASE_DIR)
ADJANGO_APPS_PREPATH = get_setting('ADJANGO_APPS_PREPATH', None)
ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION = get_setting(
    'ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION',
    None
)
ADJANGO_CONTROLLERS_LOGGER_NAME = get_setting('ADJANGO_CONTROLLERS_LOGGER_NAME', 'global')
ADJANGO_CONTROLLERS_LOGGING = get_setting('ADJANGO_CONTROLLERS_LOGGING', False)
ADJANGO_EMAIL_LOGGER_NAME = get_setting('ADJANGO_EMAIL_LOGGER_NAME', 'email')
ADJANGO_IP_LOGGER = get_setting('ADJANGO_IP_LOGGER', None)
ADJANGO_IP_META_NAME = get_setting('ADJANGO_IP_META_NAME', None)