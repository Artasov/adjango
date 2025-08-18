# utils/celery/tasker.py
import json
from datetime import datetime

from django_celery_beat.models import CrontabSchedule, IntervalSchedule, PeriodicTask
from kombu.exceptions import OperationalError


class Tasker:
    """
    Task scheduler class for convenient Celery task management.

    @method put: Schedules task with possibility of delayed execution or immediate.
    @method cancel_task: Cancels task by ID.
    @method beat: Schedules task via Celery Beat with ability to specify intervals and schedule.
    """

    @staticmethod
    def put(
        task: callable,
        eta: datetime = None,
        countdown: int = None,
        expires: datetime = None,
        queue: str = None,
        **kwargs,
    ) -> str:
        """
        Schedules task. If eta or countdown not specified, task executes immediately. Returns task ID.

        :param task: Celery task to execute.
        :param eta: Time when task should be executed (datetime). Takes priority over countdown.
        :param countdown: How many seconds to wait before executing task, if eta not specified.
        :param expires: Time after which task should not be executed (datetime). If not specified, doesn't expire.
        :param queue: Queue to send task to.
        :param kwargs: Named arguments for task.
        :return: Returns scheduled task ID.
        """
        try:
            if not eta and not countdown:
                result = task.apply_async(kwargs=kwargs, queue=queue, expires=expires)
            elif eta:
                result = task.apply_async(
                    kwargs=kwargs, eta=eta, queue=queue, expires=expires
                )
            else:
                result = task.apply_async(
                    kwargs=kwargs, countdown=countdown, queue=queue, expires=expires
                )
        except OperationalError:
            # If the broker is unavailable, execute task locally instead of failing.
            result = task.apply(kwargs=kwargs)

        return result.id

    @staticmethod
    def cancel_task(task_id: str) -> None:
        """
        Cancels task by its ID.

        :param task_id: ID of task to cancel.
        """
        from celery.result import AsyncResult

        AsyncResult(task_id).revoke(terminate=True)

    @staticmethod
    def beat(
        task: callable,
        name: str,
        schedule_time: datetime = None,
        interval: int = None,
        crontab: dict = None,
        **kwargs,
    ) -> None:
        """
        Schedules task through Celery Beat using database for long-term execution tasks.

        :param task: Celery task to execute.
        :param name: Task name in Celery Beat.
        :param schedule_time: Time when task should be executed (datetime) for one-time tasks.
        :param interval: Task execution interval (in seconds), if this is a periodic task.
        :param crontab: Task schedule using Crontab (e.g., crontab(hour=7, minute=30)).
        :param kwargs: Named arguments for the task.
        """
        if interval:
            # Schedule task with periodic interval
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=interval, period=IntervalSchedule.SECONDS
            )
        elif crontab:
            # Schedule task with Crontab schedule
            schedule, _ = CrontabSchedule.objects.get_or_create(**crontab)
        else:
            # Schedule one-time task
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=schedule_time.minute,
                hour=schedule_time.hour,
                day_of_week="*",
                day_of_month=schedule_time.day,
                month_of_year=schedule_time.month,
            )
        PeriodicTask.objects.create(
            name=name,
            task=task.name,
            crontab=schedule if not interval else None,
            interval=schedule if interval else None,
            kwargs=json.dumps(kwargs),
            one_off=not interval,  # Indicates that task is one-time if no interval is set
        )

    @staticmethod
    async def abeat(
        task: callable,
        name: str,
        schedule_time: datetime = None,
        interval: int = None,
        crontab: dict = None,
        **kwargs,
    ) -> None:
        """
        Schedules task through Celery Beat using database for long-term execution tasks.

        :param task: Celery task to execute.
        :param name: Task name in Celery Beat.
        :param schedule_time: Time when task should be executed (datetime) for one-time tasks.
        :param interval: Task execution interval (in seconds), if this is a periodic task.
        :param crontab: Task schedule using Crontab (e.g., crontab(hour=7, minute=30)).
        :param kwargs: Named arguments for the task.
        """
        if interval:
            # Schedule task with periodic interval
            schedule, _ = await IntervalSchedule.objects.aget_or_create(
                every=interval, period=IntervalSchedule.SECONDS
            )
        elif crontab:
            # Schedule task with Crontab schedule
            schedule, _ = await CrontabSchedule.objects.aget_or_create(**crontab)
        else:
            # Schedule one-time task
            schedule, _ = await CrontabSchedule.objects.aget_or_create(
                minute=schedule_time.minute,
                hour=schedule_time.hour,
                day_of_week="*",
                day_of_month=schedule_time.day,
                month_of_year=schedule_time.month,
            )
        await PeriodicTask.objects.acreate(
            name=name,
            task=task.name,
            crontab=schedule if not interval else None,
            interval=schedule if interval else None,
            kwargs=json.dumps(kwargs),
            one_off=not interval,  # Indicates that task is one-time if no interval is set
        )
