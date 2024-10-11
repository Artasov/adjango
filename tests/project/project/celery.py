from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(
    worker_concurrency=5,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
    worker_max_tasks_per_child=50,
    broker_transport_options={
        'max_retries': 3, 'interval_start': 0,
        'interval_step': 0.5, 'interval_max': 2
    },
)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
