# management/commands/celerypurge.py
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from adjango.utils.celery.app import resolve_celery_app


class Command(BaseCommand):
    help = "Purge Celery queues (all queues by default, or specific one if --queue is specified)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--queue",
            type=str,
            help="Name of specific queue to purge (if not specified, all queues are purged)",
        )

    def handle(self, *args, **options):
        try:
            # Initialize Celery app dynamically
            app = resolve_celery_app()

            queue_name = options["queue"]
            # If queue is not specified, purge all queues
            purge_all = queue_name is None

            # Perform purge operation
            with app.connection() as connection:
                if purge_all:
                    # Get list of all queues
                    try:
                        # Use standard queues
                        queues_to_purge = ["default", "celery"]

                        # Add additional queues from settings if available
                        if hasattr(settings, "CELERY_TASK_ROUTES"):
                            for route_config in settings.CELERY_TASK_ROUTES.values():
                                if isinstance(route_config, dict) and "queue" in route_config:
                                    queue = route_config["queue"]
                                    if queue not in queues_to_purge:
                                        queues_to_purge.append(queue)

                        total_purged = 0
                        for queue in queues_to_purge:
                            try:
                                purged = connection.default_channel.queue_purge(queue)
                                if purged is not None and purged > 0:
                                    total_purged += purged
                                    self.stdout.write(self.style.SUCCESS(f'Queue "{queue}": deleted {purged} tasks'))
                            except Exception as e:
                                # Queue may not exist - this is normal
                                if "NOT_FOUND" not in str(e):
                                    self.stdout.write(self.style.WARNING(f'Error purging queue "{queue}": {e}'))

                        self.stdout.write(self.style.SUCCESS(f"Total deleted tasks: {total_purged}"))

                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error purging all queues: {e}"))
                        sys.exit(1)

                else:
                    # Purge specific queue
                    try:
                        purged = connection.default_channel.queue_purge(queue_name)
                        if purged is not None:
                            self.stdout.write(
                                self.style.SUCCESS(f'Queue "{queue_name}" purged. Deleted tasks: {purged}')
                            )
                        else:
                            self.stdout.write(self.style.WARNING(f'Queue "{queue_name}" is empty or does not exist'))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f'Error purging queue "{queue_name}": {e}'))
                        sys.exit(1)

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error connecting to Celery: {e}"))
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS("Purge operation completed successfully."))
