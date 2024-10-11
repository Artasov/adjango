from __future__ import annotations

from pprint import pprint
from typing import Any

import aiohttp
from asgiref.sync import sync_to_async
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.db.transaction import Atomic


class AsyncAtomicContextManager(Atomic):
    """
    Асинхронный контекст-менеджер для работы с транзакциями.

    @method __aenter__: Асинхронный вход в контекст менеджера транзакции.
    @method __aexit__: Асинхронный выход из контекста менеджера транзакции.
    """

    def __init__(self, using: str | None = None, savepoint: bool = True, durable: bool = False):
        """
        Инициализация асинхронного атомарного контекст-менеджера.

        @param using: Название базы данных, которая будет использоваться.
        @param savepoint: Определяет, будет ли использоваться savepoint.
        @param durable: Флаг для долговечных транзакций.
        """
        super().__init__(using, savepoint, durable)

    async def __aenter__(self) -> AsyncAtomicContextManager:
        """
        Асинхронно входит в транзакционный контекст.

        @return: Возвращает контекст менеджера.
        """
        await sync_to_async(super().__enter__)()
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback) -> None:
        """
        Асинхронно выходит из транзакционного контекста.

        @param exc_type: Тип исключения, если оно возникло.
        @param exc_value: Объект исключения, если оно возникло.
        @param traceback: Стек вызовов, если возникло исключение.

        @return: None
        """
        await sync_to_async(super().__exit__)(exc_type, exc_value, traceback)


async def download_file_to_temp(url: str) -> ContentFile:
    """
    Асинхронно скачивает файл с указанного URL и сохраняет его в объект ContentFile в памяти.

    @param url: URL файла, который нужно скачать.
    @return: Объект ContentFile с содержимым скачанного файла.

    @raises ValueError: Если скачивание не удалось (код ответа не 200).
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                file_content = await response.read()
                file_name = url.split('/')[-1]
                return ContentFile(file_content, name=file_name)
            raise ValueError(f"Failed to download image from {url}, status code: {response.status}")


def add_user_to_group(user: Any, group_name: str) -> None:
    """
    Добавляет пользователя в указанную группу.

    @param user: Пользователь, которого нужно добавить в группу.
    @param group_name: Имя группы, в которую нужно добавить пользователя.

    @return: None
    """
    group, created = Group.objects.get_or_create(name=group_name)
    if user not in group.user_set.all():
        group.user_set.add(user)


async def apprint(*args: Any, **kwargs: Any) -> None:
    """ Асинхронно выводит данные с использованием pprint. """
    await sync_to_async(pprint)(*args, **kwargs)
