import pytest

from adjango.utils.funcs import aadd, aall, aset


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_related_manager_async_methods_and_polymorphic_manager():
    from app.models import Order, Product, User

    user = await User.objects.acreate(username='async_u', phone='100')
    order = await Order.objects.acreate(user=user)

    product, created = await Product.objects.aget_or_create(name='p', price=1)
    assert created

    await aset(order.products, [product])
    related = await aall(order.products)
    assert related == [product]
    assert all(isinstance(p, Product) for p in related)

    await aset(order.products, [])
    await aadd(order.products, product)
    assert await aall(order.products) == [product]

    order2, created2 = await Order.objects.aget_or_create(user=user)
    assert order2 == order and not created2

    orders = await aall(Order.objects.prefetch_related('products'))
    assert order in orders
