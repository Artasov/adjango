from __future__ import annotations

from functools import wraps
from typing import Any, Type
from urllib.parse import urlparse

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.files.base import ContentFile
from django.db.models import QuerySet, Model, Manager
from django.db.transaction import Atomic
from django.shortcuts import resolve_url, redirect

from adjango.utils.base import download_file_to_temp


class AsyncAtomicContextManager(Atomic):
    def __init__(self, using=None, savepoint=True, durable=False):
        super().__init__(using, savepoint, durable)

    async def __aenter__(self):
        await sync_to_async(super().__enter__)()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await sync_to_async(super().__exit__)(exc_type, exc_value, traceback)


def aatomic(view_func):
    @wraps(view_func)
    async def _wrapped_view(request, *args, **kwargs):
        async with AsyncAtomicContextManager():
            return await view_func(request, *args, **kwargs)

    return _wrapped_view


async def aget(
        queryset: QuerySet,
        exception: Type[Exception] | None = None,
        *args: Any,
        **kwargs: Any,

) -> Model | None:
    """
    Асинхронно получает единственный объект из заданного QuerySet, соответствующий переданным параметрам.

    @param queryset: QuerySet, из которого нужно получить объект.
    @param exception: Класс исключения, которое будет выброшено, если объект не найден. Если None, возвращается None.

    @return: Объект модели или None, если объект не найден и exception не задан.

    @raises exception: Если объект не найден и передан класс исключения.

    @behavior:
        - Пытается асинхронно получить объект с помощью queryset.aget().
        - Если объект не найден, обрабатывает исключение DoesNotExist.
        - Если exception is not None, выбрасывает указанное исключение.
        - Если exception is None, возвращает None.

    @usage:
        result = await aget(MyModel.objects, MyCustomException, id=1)
    """
    try:
        return await queryset.aget(*args, **kwargs)
    except queryset.model.DoesNotExist:
        if exception is not None:
            raise exception()
    return None


async def arelated(model_object, related_field_name: str) -> object or None:
    return await sync_to_async(getattr)(model_object, related_field_name, None)


async def aadd(queryset, data, *args, **kwargs):
    return await sync_to_async(queryset.add)(data, *args, **kwargs)


async def aall(objects: Manager) -> list:
    return await sync_to_async(list)(objects.all())


async def afilter(queryset, *args, **kwargs) -> list:
    """
    This function is used to filter objects...
    :param queryset:
    :param args:
    :param kwargs:
    :return: List of ...
    """
    return await sync_to_async(list)(queryset.filter(*args, **kwargs))


def auser_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
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
            # If the login_url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            return redirect(login_url)

        return _wrapped_view

    return decorator


def alogin_required(
        function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = auser_passes_test(
        sync_to_async(lambda u: u.is_authenticated),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


async def set_image_by_url(model_obj: Model, field_name: str, image_url: str) -> None:
    """
    Загружает изображение с заданного URL и устанавливает его в указанное поле модели без
    предварительного сохранения файла на диск.

    @param model_obj: Экземпляр модели, в который нужно установить изображение.
    @param field_name: Название поля, в которое нужно сохранить изображение.
    @param image_url: URL изображения, которое нужно загрузить.
    @return: None
    """
    # Скачиваем изображение как объект ContentFile
    image_file: ContentFile = await download_file_to_temp(image_url)

    # Используем setattr, чтобы установить файл в поле модели
    await sync_to_async(getattr(model_obj, field_name).save)(image_file.name, image_file)
    await model_obj.asave()
