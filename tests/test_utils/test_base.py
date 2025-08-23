from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.timezone import now

from adjango.utils.base import (
    AsyncAtomicContextManager,
    add_user_to_group,
    apprint,
    build_full_url,
    calculate_age,
    decrease_by_percentage,
    diff_by_timedelta,
    download_file_to_temp,
    get_plural_form_number,
    is_async_context,
    is_email,
    is_phone,
    phone_format,
)


@pytest.mark.asyncio
async def test_is_async_context_async():
    assert is_async_context()


def test_is_async_context_sync():
    assert not is_async_context()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_async_atomic_context_manager():
    User = get_user_model()
    async with AsyncAtomicContextManager():
        await User.objects.acreate(username='john', phone='123')
    user = await User.objects.aget(username='john')
    assert user.phone == '123'


@pytest.mark.django_db
def test_add_user_to_group():
    User = get_user_model()
    user = User.objects.create_user(username='u', phone='100', password='p')
    add_user_to_group(user, 'test')
    group = Group.objects.get(name='test')
    assert group.user_set.filter(pk=user.pk).exists()


@pytest.mark.django_db
def test_build_full_url(settings):
    settings.DOMAIN_URL = 'https://example.com'
    url = build_full_url('admin:index')
    assert url == 'https://example.com/admin/'


def test_calculate_age():
    birth = date.today().replace(year=date.today().year - 20)
    assert calculate_age(birth) == 20


def test_calculate_age_before_birthday():
    import calendar

    today = date.today()
    birth_year = today.year - 20
    next_month = today.month + 1
    if next_month > 12:
        next_month = 1
        birth_year += 1
    day = min(today.day, calendar.monthrange(birth_year, next_month)[1])
    birth = date(birth_year, next_month, day)
    assert calculate_age(birth) == 19


def test_is_phone():
    assert is_phone('+1 (234) 567-8901')
    assert not is_phone('123-abc')


def test_is_email():
    assert is_email('test@example.com')
    assert not is_email('bad-email')


def test_phone_format():
    assert phone_format('+1 (234) 567-8901') == '12345678901'


def test_diff_by_timedelta():
    td = timedelta(hours=1)
    res = diff_by_timedelta(td)
    diff = res - now()
    assert abs(diff.total_seconds() - td.total_seconds()) < 1


def test_decrease_by_percentage():
    assert decrease_by_percentage(100, 10) == 90


def test_get_plural_form_number():
    forms = ('apple', 'apples', 'apples')
    assert get_plural_form_number(1, forms) == 'apple'
    assert get_plural_form_number(2, forms) == 'apples'
    assert get_plural_form_number(5, forms) == 'apples'


@pytest.mark.asyncio
async def test_download_file_to_temp(monkeypatch):
    from types import SimpleNamespace

    class FakeResponse(SimpleNamespace):
        status = 200

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def read(self):
            return b'data'

    class FakeSession(SimpleNamespace):
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def get(self, url):
            return FakeResponse()

    monkeypatch.setattr('adjango.utils.base.aiohttp.ClientSession', lambda: FakeSession())
    file = await download_file_to_temp('http://example.com/file.txt')
    assert file.name == 'file.txt'
    assert file.read() == b'data'


@pytest.mark.asyncio
async def test_download_file_to_temp_error(monkeypatch):
    from types import SimpleNamespace

    class FakeResponse(SimpleNamespace):
        status = 404

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def read(self):
            return b''

    class FakeSession(SimpleNamespace):
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def get(self, url):
            return FakeResponse()

    monkeypatch.setattr('adjango.utils.base.aiohttp.ClientSession', lambda: FakeSession())
    with pytest.raises(ValueError):
        await download_file_to_temp('http://example.com/file.txt')


@pytest.mark.asyncio
async def test_apprint(monkeypatch):
    calls = {}

    def fake_pprint(*args, **kwargs):
        calls['args'] = args
        calls['kwargs'] = kwargs

    monkeypatch.setattr('adjango.utils.base.pprint', fake_pprint)
    await apprint('data', key='value')
    assert calls['args'] == ('data',)
    assert calls['kwargs'] == {'key': 'value'}
