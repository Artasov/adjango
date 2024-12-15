# utils/base.py
from __future__ import annotations

import asyncio
import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from pprint import pprint
from typing import Any, Union, Tuple

import aiohttp
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.db.transaction import Atomic
from django.urls import reverse
from django.utils.timezone import now


def is_async_context() -> bool:
    """
    Проверяет, выполняется ли код в асинхронном контексте.
    """
    try:
        loop = asyncio.get_running_loop()
        return loop.is_running()
    except RuntimeError:
        return False


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


def build_full_url(pattern_name: str, *args: Any, **kwargs: Any) -> str:
    """
    Строит полный URL на основе имени шаблона и переданных аргументов.

    :param pattern_name: Имя URL-шаблона.
    :param args: Позиционные аргументы для URL.
    :param kwargs: Ключевые аргументы для URL.
    :return: Полный URL как строка.
    """
    relative_url = reverse(pattern_name, args=args, kwargs=kwargs)
    full_url = f"{settings.DOMAIN_URL.rstrip('/')}{relative_url}"
    return full_url


def calculate_age(birth_date: date) -> int:
    """
    Вычисляет возраст на основе даты рождения.

    :param birth_date: Дата рождения.
    :return: Возраст в годах.
    """
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def is_phone(phone: str) -> bool:
    """
    Проверяет, соответствует ли строка формату телефонного номера.

    :param phone: Строка для проверки.
    :return: True, если строка является допустимым телефонным номером, иначе False.
    """
    pattern = re.compile(r'^\+?[\d\s\-()]{7,15}$')
    cleaned_phone = re.sub(r'\s+', '', phone)
    return bool(pattern.match(cleaned_phone))


def is_email(email: str) -> bool:
    """
    Проверяет, соответствует ли строка формату email-адреса.

    :param email: Строка для проверки.
    :return: True, если строка является допустимым email-адресом, иначе False.
    """
    pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    return bool(pattern.match(email))


def phone_format(phone: str) -> str:
    """
    Форматирует телефонный номер, убирая все символы, кроме цифр.

    :param phone: Исходный телефонный номер.
    :return: Отформатированный телефонный номер.
    """
    return re.sub(r'\D', '', phone)


def diff_by_timedelta(timedelta_obj: timedelta) -> datetime:
    """
    Вычисляет новую дату и время, добавляя заданный интервал к текущему времени.

    :param timedelta_obj: Объект timedelta для добавления.
    :return: Новая дата и время.
    """
    return now() + timedelta_obj


def decrease_by_percentage(
        num: Union[int, float, Decimal],
        percent: Union[int, float, Decimal]
) -> Decimal:
    """
    Уменьшает число на заданный процент с высокой точностью.

    :param num: Число, которое нужно уменьшить.
    :param percent: Процент уменьшения.
    :return: Число после уменьшения на заданный процент.
    """
    num_dec = Decimal(num)
    percent_dec = Decimal(percent)
    result = num_dec * (Decimal(1) - percent_dec / Decimal(100))
    return result.quantize(Decimal('1.00'))  # Настройте точность по необходимости


def get_plural_form_number(number: int, forms: Tuple[str, str, str]) -> str:
    """
    Возвращает правильную форму слова в зависимости от числа.

    Пример: get_plural_form_number(minutes, ('минуту', 'минуты', 'минут'))

    :param number: Число для определения формы.
    :param forms: Кортеж из трёх форм слова.
    :return: Правильная форма слова.
    """
    if number % 10 == 1 and number % 100 != 11:
        return forms[0]
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return forms[1]
    else:
        return forms[2]
