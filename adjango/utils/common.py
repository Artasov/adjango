# utils/common.py
import os
import sys
import traceback
from typing import Generator, Any, Protocol, TYPE_CHECKING

from django.apps import apps

if TYPE_CHECKING:
    from django.db.models import Model


class _UserWithNameProtocol(Protocol):
    """Protocol for user models with name attributes."""

    first_name: str
    last_name: str
    username: str


def get_full_name(user: _UserWithNameProtocol) -> str:
    """
    Returns user's full name in "Last Name First Name" format.
    Works with any user model (custom or Django's AbstractUser) that has
    first_name, last_name, and username attributes.

    If first_name is missing, returns only last name.
    If last_name is missing, returns only first name.
    If both name fields are empty, returns username.

    :param user: User model instance with name attributes
    :return: Full name string
    """
    # Both last name and first name are set
    if getattr(user, 'last_name', None) and getattr(user, 'first_name', None):
        full_name = f"{user.last_name} {user.first_name}"
        return full_name

    # Only last name is set
    if getattr(user, 'last_name', None):
        return user.last_name

    # Only first name is set
    if getattr(user, 'first_name', None):
        return user.first_name

    # Neither name field is set - return username
    return getattr(user, 'username', '')


def is_celery() -> bool:
    """
    Checks if process is running in Celery context.

    :return: True if Celery is running, otherwise False.

    @behavior:
        - Checks if first sys.argv argument contains 'celery', indicating Celery startup.
        - Also checks for IS_CELERY environment variable which can be set to indicate
          that process is part of Celery.

    @usage:
        if is_celery():
            # Logic for execution inside Celery process
    """
    return 'celery' in sys.argv[0] or bool(os.getenv('IS_CELERY', False))


def traceback_str(error: BaseException) -> str:
    """
    Converts exception object to string representation of full call stack.

    :param error: Exception object.

    :return: String with full call stack related to exception.

    @usage:
        try:
            ...
        except Exception as e:
            log.error(traceback_str(e))
    """
    return ''.join(traceback.format_exception(type(error), error, error.__traceback__))


def get_models_list() -> Generator[str, Any, None]:
    """
    Returns a generator of strings in 'app.Model' format for all registered models.
    """
    models = apps.get_models()
    return (f'{model._meta.app_label}.{model.__name__}' for model in models)  # noqa
