# management/commands/celerybeat.py
try:
    from celery import current_app
    from django.core.management.base import BaseCommand
    from django_celery_beat.schedulers import DatabaseScheduler

    from adjango.utils.celery.app import resolve_celery_app

    class Command(BaseCommand):
        help = "Starts Celery Beat scheduler"

        def add_arguments(self, parser):
            parser.add_argument(
                "--loglevel", default="INFO", help="Logging level (default: INFO)"
            )
            parser.add_argument(
                "--scheduler",
                default="django_celery_beat.schedulers:DatabaseScheduler",
                help="Scheduler class (default: DatabaseScheduler)",
            )

        def handle(self, *args, **options):
            try:
                self.stdout.write(
                    self.style.SUCCESS("Starting Celery Beat scheduler...")
                )
                # Ensure Celery app is initialized for arbitrary project layout
                app = resolve_celery_app()
                beat = current_app.Beat(
                    scheduler=DatabaseScheduler,
                    loglevel=options["loglevel"],
                )
                beat.run()
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING("Received stop signal. Shutting down...")
                )
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error starting Celery Beat: {e}"))

except ImportError:
    pass
