from django.http import HttpResponse
from django.urls import path

from adjango.utils.celery.tasker import Tasker
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
        countdown=countdown_time  # Задача будет выполнена через 30 секунд
    )

    return HttpResponse(f'<h1>{r.ip}</h1><p>Task scheduled with ID: {task_id}</p>')


urlpatterns = [path('', view), ]
