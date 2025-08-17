from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from adjango.utils.celery.tasker import Tasker


def test_tasker_put_variants():
    dummy_task = Mock()
    dummy_task.apply_async.return_value = SimpleNamespace(id="123")

    task_id = Tasker.put(dummy_task, countdown=10, queue="q", param=1)
    assert task_id == "123"
    dummy_task.apply_async.assert_called_with(kwargs={"param": 1}, countdown=10, queue="q", expires=None)

    dummy_task.apply_async.reset_mock()
    eta = datetime(2024, 1, 1)
    Tasker.put(dummy_task, eta=eta)
    dummy_task.apply_async.assert_called_with(kwargs={}, eta=eta, queue=None, expires=None)

    dummy_task.apply_async.reset_mock()
    Tasker.put(dummy_task)
    dummy_task.apply_async.assert_called_with(kwargs={}, queue=None, expires=None)


def test_tasker_cancel_task():
    with patch("celery.result.AsyncResult") as async_result:
        Tasker.cancel_task("abc")
        async_result.assert_called_with("abc")
        async_result.return_value.revoke.assert_called_once_with(terminate=True)


@pytest.mark.django_db
def test_tasker_beat_interval():
    dummy_task = SimpleNamespace(name="task.name")
    with (
        patch(
            "adjango.utils.celery.tasker.IntervalSchedule.objects.get_or_create",
            return_value=(Mock(), True),
        ) as get_or_create,
        patch("adjango.utils.celery.tasker.PeriodicTask.objects.create") as create,
    ):
        Tasker.beat(dummy_task, name="t1", interval=10)
        get_or_create.assert_called_once()
        create.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_tasker_abeat_interval():
    dummy_task = SimpleNamespace(name="task.name")
    with (
        patch(
            "adjango.utils.celery.tasker.IntervalSchedule.objects.aget_or_create",
            new_callable=AsyncMock,
            return_value=(Mock(), True),
        ) as aget_or_create,
        patch(
            "adjango.utils.celery.tasker.PeriodicTask.objects.acreate",
            new_callable=AsyncMock,
        ) as acreate,
    ):
        await Tasker.abeat(dummy_task, name="t1", interval=10)
        aget_or_create.assert_called_once()
        acreate.assert_called_once()

