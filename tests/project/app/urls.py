# app/urls.py
from pprint import pprint

from django.http import HttpResponse
from django.urls import path

from adjango.utils.celery.tasker import Tasker
from adjango.utils.funcs import aall, afilter, aset
from .models import Order, Product, User
from .tasks import test_task

app_name = 'app'


def view(r):
    # Example of task scheduling using Tasker
    countdown_time = 10  # Execute task in 30 seconds

    task_id = Tasker.put(
        task=test_task,
        param1='param1',
        param2=69,
        param3={'key': 'value'},
        countdown=countdown_time,
    )

    return HttpResponse(f'<h1>{r.ip}</h1><p>Task scheduled with ID: {task_id}</p>')


async def view_test_arelated(request):
    # Simply search or create the same order object each time
    product, _ = await Product.objects.aget_or_create(name='TEST1', price=100)
    order, _ = await Order.objects.aget_or_create(user=request.user)
    user = await User.objects.alast()
    roles = await user.roles

    pprint(order.user)
    await aset(order.products, [product])
    # Get order without related objects
    orders_ = await afilter(Order.objects, user=request.user)
    # Asynchronously get related objects.
    order.user = await order.arelated('user')
    order = await Order.objects.aget(user=request.user)
    products = await aall(order.products)
    products_qs = order.products.all()
    orders = await aall(Order.objects.prefetch_related('products'))
    for o in orders:
        for p in o.products.all():
            print(p.id)
    return HttpResponse(f'ok: {len(orders_)} {len(products)}')


async def view_test_service(_):
    product, _ = await Product.objects.aget_or_create(name='TEST1', price=100)
    if product.service.is_valid_price():
        return HttpResponse('Price is valid')
    else:
        return HttpResponse('Price is invalid')


urlpatterns = [
    path('view_task_test', view),
    path('view_test_service', view_test_service),
    path('view_test_arelated', view_test_arelated),
]
