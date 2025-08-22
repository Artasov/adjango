import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from adjango.utils.funcs import (
    aadd,
    aall,
    afilter,
    agetorn,
    arelated,
    aset,
    auser_passes_test,
    getorn,
)


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_getorn_and_agetorn():
    from app.models import Product

    p = await Product.objects.acreate(name="p1", price=10)
    from asgiref.sync import sync_to_async

    assert await sync_to_async(getorn)(Product.objects, None, name="p1") == p
    assert await sync_to_async(getorn)(Product.objects, None, name="missing") is None

    p_async = await agetorn(Product.objects, None, name="p1")
    assert p_async == p
    assert await agetorn(Product.objects, None, name="missing") is None

    class MyError(Exception):
        pass

    with pytest.raises(MyError):
        await sync_to_async(getorn)(Product.objects, MyError, name="missing")

    with pytest.raises(MyError):
        await agetorn(Product.objects, MyError, name="missing")


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_agetorn_after_only():
    from app.models import Product

    p = await Product.objects.acreate(name="p_only", price=10)
    result = await Product.objects.only("name").agetorn(id=p.id)
    assert result == p


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_arelated_aset_aadd_aall_afilter():
    from app.models import Order, Product, User

    user = await User.objects.acreate(username="u", phone="200")
    order = await Order.objects.acreate(user=user)
    p1 = await Product.objects.acreate(name="p1", price=1)
    p2 = await Product.objects.acreate(name="p2", price=2)

    await aset(order.products, [p1, p2])
    related = await order.products.aall()
    assert set(related) == {p1, p2}

    await aset(order.products, [])
    await aadd(order.products, p1)
    assert await order.products.aall() == [p1]

    all_products = await aall(Product.objects)
    assert p1 in all_products and p2 in all_products

    filtered = await afilter(Product.objects, name="p1")
    assert all(prod.name == "p1" for prod in filtered)

    related_user = await arelated(order, "user")
    assert related_user == user


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_arelated_errors():
    from app.models import Order, User

    user = await User.objects.acreate(username="u3", phone="3")

    # Test with non-existent field
    with pytest.raises(ValueError):
        await arelated(user, "nonexistent_field")

    # Test successful related access
    order = await Order.objects.acreate(user_id=user.pk)
    order_fresh = await Order.objects.aget(pk=order.pk)
    related = await arelated(order_fresh, "user")
    assert related == user


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_auser_passes_test():
    from app.models import User

    async def ok(user):
        return True

    async def fail(user):
        return False

    @auser_passes_test(ok)
    async def ok_view(request):
        return HttpResponse("ok")

    @auser_passes_test(fail)
    async def fail_view(request):
        return HttpResponse("fail")

    rf = RequestFactory()
    req = rf.get("/")
    req.user = await User.objects.acreate(username="u2", phone="2")

    resp = await ok_view(req)
    assert resp.status_code == 200

    resp_fail = await fail_view(req)
    assert resp_fail.status_code == 302
    assert "/login/" in resp_fail["Location"]


@pytest.mark.asyncio
async def test_set_image_by_url(monkeypatch):
    from django.core.files.base import ContentFile

    from adjango.utils.funcs import set_image_by_url

    async def fake_download(url):
        return ContentFile(b"img", name="img.png")

    monkeypatch.setattr("adjango.utils.funcs.download_file_to_temp", fake_download)

    class DummyField:
        def __init__(self):
            self.saved = None

        def save(self, name, content):
            self.saved = (name, content.read())

    class DummyModel:
        def __init__(self):
            self.image = DummyField()
            self.saved = False

        async def asave(self):
            self.saved = True

    obj = DummyModel()
    await set_image_by_url(obj, "image", "http://example.com/img.png")
    assert obj.image.saved[0] == "img.png"
    assert obj.image.saved[1] == b"img"
    assert obj.saved
