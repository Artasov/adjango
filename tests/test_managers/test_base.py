import pytest
from django.contrib.auth import get_user_model


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_acreate_user():
    User = get_user_model()
    user = await User.objects.acreate_user(username='async', phone='1', password='pwd')
    fetched = await User.objects.aget(pk=user.pk)
    assert fetched.username == 'async'
