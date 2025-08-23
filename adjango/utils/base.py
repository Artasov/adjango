# utils/base.py
from __future__ import annotations

import asyncio
import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from pprint import pprint
from typing import Any, Tuple, Union

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
    Checks if code is running in an async context.
    """
    try:
        loop = asyncio.get_running_loop()
        return loop.is_running()
    except RuntimeError:
        return False


class AsyncAtomicContextManager(Atomic):
    """
    Asynchronous context manager for working with transactions.

    @method __aenter__: Asynchronous entry into transaction context manager.
    @method __aexit__: Asynchronous exit from transaction context manager.
    """

    def __init__(self, using: str | None = None, savepoint: bool = True, durable: bool = False):
        """
        Initialize asynchronous atomic context manager.

        :param using: Database name to be used.
        :param savepoint: Determines whether savepoint will be used.
        :param durable: Flag for durable transactions.
        """
        super().__init__(using, savepoint, durable)

    async def __aenter__(self) -> AsyncAtomicContextManager:
        """
        Async entry into transaction context.

        :return: Returns context manager.
        """
        await sync_to_async(super().__enter__)()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback,
    ) -> None:
        """
        Async exit from transaction context.

        :param exc_type: Exception type if one occurred.
        :param exc_value: Exception object if one occurred.
        :param traceback: Call stack if exception occurred.

        :return: None
        """
        await sync_to_async(super().__exit__)(exc_type, exc_value, traceback)


async def download_file_to_temp(url: str) -> ContentFile:
    """
    Async download file from specified URL and save it to ContentFile object in memory.

    :param url: URL of file to download.
    :return: ContentFile object with downloaded file content.

    @raises ValueError: If download failed (response code not 200).
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                file_content = await response.read()
                file_name = url.split("/")[-1]
                return ContentFile(file_content, name=file_name)
            raise ValueError(f'Failed to download image from {url}, status code: {response.status}')


def add_user_to_group(user: Any, group_name: str) -> None:
    """
    Adds user to specified group.

    :param user: User to add to group.
    :param group_name: Name of group to add user to.
    """
    group, created = Group.objects.get_or_create(name=group_name)
    # More efficient check using exists()
    if not group.user_set.filter(pk=user.pk).exists():
        group.user_set.add(user)


async def apprint(*args: Any, **kwargs: Any) -> None:
    """Async print data using pprint."""
    await sync_to_async(pprint)(*args, **kwargs)


def build_full_url(pattern_name: str, *args: Any, **kwargs: Any) -> str:
    """
    Builds full URL based on pattern name and passed arguments.

    :param pattern_name: URL pattern name.
    :param args: Positional arguments for URL.
    :param kwargs: Keyword arguments for URL.
    :return: Full URL as string.
    """
    relative_url = reverse(pattern_name, args=args, kwargs=kwargs)
    full_url = f'{settings.DOMAIN_URL.rstrip("/")}{relative_url}'
    return full_url


def calculate_age(birth_date: date) -> int:
    """
    Calculates age based on birth date.

    :param birth_date: Birth date.
    :return: Age in years.
    """
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def is_phone(phone: str) -> bool:
    """
    Checks if string matches phone number format.

    :param phone: String to check.
    :return: True if string is valid phone number, otherwise False.
    """
    pattern = re.compile(r'^\+?[\d\s\-()]{7,15}$')
    cleaned_phone = re.sub(r'\s+', '', phone)
    return bool(pattern.match(cleaned_phone))


def is_email(email: str) -> bool:
    """
    Checks if string matches email format.

    :param email: String to check.
    :return: True if string is valid email address, otherwise False.
    """
    pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    return bool(pattern.match(email))


def phone_format(phone: str) -> str:
    """
    Formats phone number by removing all characters except digits.

    :param phone: Original phone number.
    :return: Formatted phone number containing only digits.
    """
    return re.sub(r'\D', '', phone)


def normalize_phone(phone: str, country_code: str = "+7") -> str:
    """
    Normalizes phone number to international format.

    :param phone: Phone number to normalize
    :param country_code: Default country code to use
    :return: Normalized phone number
    """
    # Remove all non-digits
    digits_only = phone_format(phone)

    if not digits_only:
        return ''

    # Handle Russian phone numbers
    if country_code == "+7":
        if digits_only.startswith('8') and len(digits_only) == 11:
            # Replace leading 8 with 7
            digits_only = '7' + digits_only[1:]
        elif digits_only.startswith('7') and len(digits_only) == 11:
            # Already in correct format
            pass
        elif len(digits_only) == 10:
            # Add country code
            digits_only = '7' + digits_only

    return "+" + digits_only


def diff_by_timedelta(timedelta_obj: timedelta) -> datetime:
    """
    Calculates new date and time by adding specified interval to current time.

    :param timedelta_obj: Timedelta object to add.
    :return: New date and time.
    """
    return now() + timedelta_obj


def decrease_by_percentage(num: Union[int, float, Decimal], percent: Union[int, float, Decimal]) -> Decimal:
    """
    Decreases number by specified percentage with high precision.

    :param num: Number to decrease.
    :param percent: Percentage to decrease by.
    :return: Number after decreasing by specified percentage.
    """
    num_dec = Decimal(num)
    percent_dec = Decimal(percent)
    result = num_dec * (Decimal(1) - percent_dec / Decimal(100))
    return result.quantize(Decimal('1.00'))  # Adjust precision as needed


def get_plural_form_number(number: int, forms: Tuple[str, str, str]) -> str:
    """
    Returns correct word form depending on number.

    Example: get_plural_form_number(minutes, ('minute', 'minutes', 'minutes'))

    :param number: Number to determine form for.
    :param forms: Tuple of three word forms.
    :return: Correct word form.
    """
    if number % 10 == 1 and number % 100 != 11:
        return forms[0]
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return forms[1]
    else:
        return forms[2]
