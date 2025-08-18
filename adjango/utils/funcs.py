# utils/funcs.py
from __future__ import annotations

from functools import wraps
from typing import Any, Optional, Type
from urllib.parse import urlparse

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import SynchronousOnlyOperation
from django.core.files.base import ContentFile
from django.db.models import Manager, Model, QuerySet
from django.shortcuts import resolve_url

from adjango.utils.base import download_file_to_temp


def getorn(
    queryset: QuerySet,
    exception: Type[Exception] | None = None,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Gets single object from given QuerySet matching passed parameters.

    :param queryset: QuerySet to get object from.
    :param exception: Exception class to raise if object not found.
                      If None, returns None.

    :return: Model object or None if object not found and exception not specified.

    @behavior:
        - Tries to get object using queryset.get().
        - If object not found, raises exception or returns None.

    @usage:
        result = getorn(MyCustomException, id=1)
    """
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        if exception is not None:
            raise exception()
    return None


async def agetorn(
    queryset: QuerySet,
    exception: Type[Exception] | None = None,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Async gets single object from given QuerySet matching passed parameters.

    :param queryset: QuerySet to get object from.
    :param exception: Exception class to raise if object not found.
                      If None, returns None.

    :return: Model object or None if object not found and exception not specified.

    @behavior:
        - Tries to async get object using queryset.aget().
        - If object not found, raises exception or returns None.

    @usage:
        result = await agetorn(MyCustomException, id=1)
    """
    try:
        return await queryset.aget(*args, **kwargs)
    except queryset.model.DoesNotExist:
        if exception is not None:
            raise exception()
    return None


async def arelated(obj: Model, field: str) -> Any:
    """
    Async gets related object from model by specified related field name.

    :param obj: Model instance to get related object from.
    :param field: Name of related field to get object from.

    :return: Related object or None if field doesn't exist.

    @usage: result = await arelated(my_model_instance, "related_field_name")
    """
    try:
        value = getattr(obj, field)
        return value
    except AttributeError:
        raise ValueError(f"Field '{field}' does not exist for object '{obj.__class__.__name__}'")
    except SynchronousOnlyOperation:
        return await sync_to_async(getattr)(obj, field)


async def aset(related_manager, data, *args, **kwargs) -> None:
    """
    Set related objects for ManyToMany field asynchronously.

    Arguments:
        related_manager: Related objects manager (e.g., order.products)
        data: List or queryset of objects to set
    """
    await sync_to_async(related_manager.set)(data, *args, **kwargs)


async def aadd(objects: Manager | QuerySet, data: Any, *args: Any, **kwargs: Any) -> None:
    """
    Async adds object or data to ManyToMany field via add() method.

    :param objects: Model manager or field to add data to.
    :param data: Data or object to add.
    :param args: Additional arguments for add() method.
    :param kwargs: Additional named arguments for add() method.

    :return: None

    @usage: await aadd(my_model_instance.related_field, related_obj)
    """
    return await sync_to_async(objects.add)(data, *args, **kwargs)


async def aall(objects: Manager | QuerySet) -> list:
    """
    Async returns all objects managed by manager.

    :param objects: Model manager to get all objects from.

    :return: List of all objects from manager.

    @usage: result = await aall(MyModel.objects)
    """
    return await sync_to_async(lambda: list(objects.all()))()


async def afilter(queryset: QuerySet, *args: Any, **kwargs: Any) -> list:
    """
    Async filters objects from QuerySet by given parameters.

    :param queryset: QuerySet to filter.
    :param args: Additional positional arguments for filtering.
    :param kwargs: Named arguments for filtering.

    :return: List of objects matching filter.

    @usage: result = await afilter(MyModel.objects, field=value)
    """
    return await sync_to_async(lambda: list(queryset.filter(*args, **kwargs)))()


def auser_passes_test(
    test_func: Any,
    login_url: Optional[str] = None,
    redirect_field_name: str = REDIRECT_FIELD_NAME,
):
    """
    Asynchronous decorator for views that checks if the user passes the test,
    redirecting to the login page if necessary.
    """
    if not login_url:
        login_url = settings.LOGIN_URL

    def decorator(view_func):
        @wraps(view_func)
        async def _wrapped_view(request, *args, **kwargs):
            if await test_func(request.user):
                return await view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url)
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if (not login_scheme or login_scheme == current_scheme) and (
                not login_netloc or login_netloc == current_netloc
            ):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(path, resolved_login_url, redirect_field_name)

        return _wrapped_view

    return decorator


async def set_image_by_url(model_obj: Model, field_name: str, image_url: str) -> None:
    """
    Downloads image from given URL and sets it to specified model field without
    preliminary saving file to disk.

    :param model_obj: Model instance to set image to.
    :param field_name: Field name to save image to.
    :param image_url: Image URL to download.
    :return: None
    """
    image_file: ContentFile = await download_file_to_temp(image_url)
    # Use setattr to set file to model field
    await sync_to_async(getattr(model_obj, field_name).save)(image_file.name, image_file)
    await model_obj.asave()
