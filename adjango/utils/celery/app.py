import importlib
import os
from typing import Optional

from celery import Celery
from django.conf import settings


def _import_app_from_path(path: str) -> Optional[Celery]:
    """Try to import Celery app from dotted path.

    Supports formats:
    - "package.module:appvar"
    - "package.module" (assumes variable name "app")
    """
    try:
        module_path, attr = (path.split(":", 1) + ["app"])[:2]
        module = importlib.import_module(module_path)
        candidate = getattr(module, attr, None)
        if isinstance(candidate, Celery):
            return candidate
    except Exception:
        return None
    return None


def resolve_celery_app() -> Celery:
    """Resolve Celery app for arbitrary Django project layout.

    Resolution order:
    1) CELERY_APP env var ("pkg.mod:app" or "pkg.mod")
    2) DJANGO_SETTINGS_MODULE → "<project>.celery:app"
    3) settings.ROOT_URLCONF → "<project>.celery:app"
    4) Fallback to Celery configured from Django settings
    """
    # 1) CELERY_APP environment variable
    celery_app_env = os.environ.get("CELERY_APP")
    if celery_app_env:
        app = _import_app_from_path(celery_app_env)
        if app is not None:
            return app

    # 2) Derive from DJANGO_SETTINGS_MODULE
    django_settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
    if django_settings_module and "." in django_settings_module:
        project_pkg = django_settings_module.rsplit(".", 1)[0]
        app = _import_app_from_path(f"{project_pkg}.celery:app")
        if app is not None:
            return app

    # 3) Derive from ROOT_URLCONF
    root_urlconf = getattr(settings, "ROOT_URLCONF", None)
    if root_urlconf and "." in root_urlconf:
        project_pkg = root_urlconf.rsplit(".", 1)[0]
        app = _import_app_from_path(f"{project_pkg}.celery:app")
        if app is not None:
            return app

    # 4) Fallback: configure Celery from Django settings
    project_name = (django_settings_module or "django").split(".", 1)[0]
    app = Celery(project_name)
    app.config_from_object("django.conf:settings", namespace="CELERY")
    try:
        app.autodiscover_tasks()
    except Exception:
        pass
    return app
