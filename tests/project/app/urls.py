# app/urls.py
from pprint import pprint

from django.http import HttpResponse
from django.urls import path

from adjango.utils.celery.tasker import Tasker

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
    await order.products.aset([product])
    # Get order without related objects
    orders_ = await Order.objects.afilter(user=request.user)
    # Asynchronously get related objects.
    order.user = await order.arelated('user')
    order = await Order.objects.aget(user=request.user)
    products = await order.products.aall()
    products_qs = order.products.all()
    orders = await Order.objects.prefetch_related('products').aall()
    for o in orders:
        for p in o.products.all():
            print(p.id)


urlpatterns = [
    path('', view),
    path('view_test_arelated/', view_test_arelated),
]
