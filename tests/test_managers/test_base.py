import pytest
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_acreate_user():
    User = get_user_model()
    if hasattr(User.objects, "acreate_user"):
        user = await User.objects.acreate_user(username='async', phone='1', password='pwd')
    else:
        user = await sync_to_async(User.objects.create_user)(username='async', phone='1', password='pwd')
    fetched = await User.objects.aget(pk=user.pk)
    assert fetched.username == 'async'
