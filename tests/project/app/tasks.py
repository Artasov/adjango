# app/tasks.py
from celery import shared_task

from adjango.decorators import task


@shared_task
@task(logger='global')
def test_task(param1: str, param2: int, param3: dict) -> bool:
    """
    Пример Celery задачи, которая принимает три параметра, включая словарь.
    """
    print(param1)
    print(param2)
    print(param3)
    return True