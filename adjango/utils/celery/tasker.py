import json
from datetime import datetime

from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule


class Tasker:
    """
    Класс планировщика задач для удобного управления задачами Celery.

    @method put: Планирует задачу с возможностью отложенного выполнения или немедленно.
    @method cancel_task: Отменяет задачу по ID.
    @method beat: Планирует задачу через Celery Beat с возможностью указания интервалов и расписания.
    """

    @staticmethod
    def put(task: callable, eta: datetime = None, countdown: int = None, expires: datetime = None,
            queue: str = None, **kwargs) -> str:
        """
        Планирует задачу. Если не указаны eta или countdown, задача выполняется немедленно. Возвращает ID задачи.

        @param task: Celery задача для выполнения.
        @param eta: Время, когда задача должна быть выполнена (datetime). Приоритетнее, чем countdown.
        @param countdown: Через сколько секунд выполнить задачу, если eta не указано.
        @param expires: Время, после которого задача не должна быть выполнена (datetime). Если не указано, не истекает.
        @param queue: Очередь, в которую нужно отправить задачу.
        @param kwargs: Именованные аргументы для задачи.
        @return: Возвращает ID запланированной задачи.
        """
        if not eta and not countdown:
            result = task.apply_async(kwargs=kwargs, queue=queue, expires=expires)
        elif eta:
            result = task.apply_async(kwargs=kwargs, eta=eta, queue=queue, expires=expires)
        else:
            result = task.apply_async(kwargs=kwargs, countdown=countdown, queue=queue, expires=expires)

        return result.id

    @staticmethod
    def cancel_task(task_id: str) -> None:
        """
        Отменяет задачу по её ID.

        @param task_id: ID задачи, которую нужно отменить.
        """
        from celery.result import AsyncResult
        AsyncResult(task_id).revoke(terminate=True)

    @staticmethod
    def beat(task: callable, name: str, schedule_time: datetime = None, interval: int = None, crontab: dict = None,
             **kwargs) -> None:
        """
        Планирует задачу через Celery Beat с использованием базы данных для задач с долгосрочным выполнением.

        @param task: Celery задача для выполнения.
        @param name: Название задачи в Celery Beat.
        @param schedule_time: Время, когда задача должна быть выполнена (datetime) для одноразовых задач.
        @param interval: Интервал выполнения задачи (в секундах), если это периодическая задача.
        @param crontab: Расписание задачи с использованием Crontab (например, crontab(hour=7, minute=30)).
        @param kwargs: Именованные аргументы для задачи.
        """
        if interval:
            # Планируем задачу с периодическим интервалом
            schedule, _ = IntervalSchedule.objects.get_or_create(every=interval, period=IntervalSchedule.SECONDS)
        elif crontab:
            # Планируем задачу с Crontab расписанием
            schedule, _ = CrontabSchedule.objects.get_or_create(**crontab)
        else:
            # Планируем одноразовую задачу
            schedule, _ = CrontabSchedule.objects.get_or_create(minute=schedule_time.minute, hour=schedule_time.hour,
                                                                day_of_week='*', day_of_month=schedule_time.day,
                                                                month_of_year=schedule_time.month)
        PeriodicTask.objects.create(
            name=name,
            task=task.name,
            crontab=schedule if not interval else None,
            interval=schedule if interval else None,
            kwargs=json.dumps(kwargs),
            one_off=not interval  # Указание, что задача одноразовая, если не задан интервал
        )

    @staticmethod
    async def abeat(task: callable, name: str, schedule_time: datetime = None, interval: int = None,
                    crontab: dict = None,
                    **kwargs) -> None:
        """
        Планирует задачу через Celery Beat с использованием базы данных для задач с долгосрочным выполнением.

        @param task: Celery задача для выполнения.
        @param name: Название задачи в Celery Beat.
        @param schedule_time: Время, когда задача должна быть выполнена (datetime) для одноразовых задач.
        @param interval: Интервал выполнения задачи (в секундах), если это периодическая задача.
        @param crontab: Расписание задачи с использованием Crontab (например, crontab(hour=7, minute=30)).
        @param kwargs: Именованные аргументы для задачи.
        """
        if interval:
            # Планируем задачу с периодическим интервалом
            schedule, _ = await IntervalSchedule.objects.aget_or_create(every=interval, period=IntervalSchedule.SECONDS)
        elif crontab:
            # Планируем задачу с Crontab расписанием
            schedule, _ = await CrontabSchedule.objects.aget_or_create(**crontab)
        else:
            # Планируем одноразовую задачу
            schedule, _ = await CrontabSchedule.objects.aget_or_create(minute=schedule_time.minute,
                                                                       hour=schedule_time.hour,
                                                                       day_of_week='*', day_of_month=schedule_time.day,
                                                                       month_of_year=schedule_time.month)
        await PeriodicTask.objects.acreate(
            name=name,
            task=task.name,
            crontab=schedule if not interval else None,
            interval=schedule if interval else None,
            kwargs=json.dumps(kwargs),
            one_off=not interval  # Указание, что задача одноразовая, если не задан интервал
        )
