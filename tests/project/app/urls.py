# app/urls.py
from pprint import pprint

from django.http import HttpResponse
from django.urls import path

from adjango.utils.celery.tasker import Tasker
from .models import Product, Order
from .tasks import test_task

app_name = 'app'


def view(r):
    # Пример планирования задачи с использованием Tasker
    countdown_time = 10  # Выполнить задачу через 30 секунд

    task_id = Tasker.put(
        task=test_task,
        param1='param1',
        param2=69,
        param3={'key': 'value'},
        countdown=countdown_time
    )

    return HttpResponse(f'<h1>{r.ip}</h1><p>Task scheduled with ID: {task_id}</p>')


async def view_test_arelated(request):
    # Просто каждый раз ищем или создаем один и тот же объект заказа
    product, _ = await Product.objects.aget_or_create(name='TEST1', price=100)
    order, _ = await Order.objects.aget_or_create(user=request.user)

    pprint(order.user)
    order: Order
    await order.products.aset([product])
    # Получаем заказ без связанных объектов
    order: Order = await Order.objects.aget(user=request.user)
    # Асинхронно получаем связанные объекты.
    order.user = await order.arelated('user')
    products = await order.products.aall()
    orders = await Order.objects.prefetch_related('products').aall()
    for o in orders:
        for p in o.products.all():
            print(p.id)


urlpatterns = [
    path('', view),
    path('view_test_arelated/', view_test_arelated),
]
