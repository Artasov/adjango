# management/commands/startbeat.py
try:
    from celery import current_app
    from django.core.management.base import BaseCommand

    from django_celery_beat.schedulers import DatabaseScheduler


    class Command(BaseCommand):
        help = 'Starts the Celery Beat Scheduler'

        def handle(self, *args, **options):
            beat = current_app.Beat(
                scheduler=DatabaseScheduler,
                loglevel='INFO',
            )
            beat.run()
except ImportError:
    pass
