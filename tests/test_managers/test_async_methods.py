import pytest


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_related_manager_async_methods_and_polymorphic_manager():
    from app.models import Order, Product, User

    user = await User.objects.acreate(username='async_u', phone='100')
    order = await Order.objects.acreate(user=user)

    product, created = await Product.objects.aget_or_create(name='p', price=1)
    assert created

    await order.products.aset([product])
    related = await order.products.aall()
    assert related == [product]
    assert all(isinstance(p, Product) for p in related)

    await order.products.aset([])
    await order.products.aadd(product)
    assert await order.products.aall() == [product]

    order2, created2 = await Order.objects.aget_or_create(user=user)
    assert order2 == order and not created2

    orders = await Order.objects.prefetch_related('products').aall()
    assert order in orders
