# management/commands/celeryworker.py
try:
    from celery import current_app
    from django.core.management.base import BaseCommand

    from adjango.utils.celery.app import resolve_celery_app

    class Command(BaseCommand):
        """
        python manage.py celeryworker --pool=solo --loglevel=info -E
        """

        help = 'Starts Celery Worker'

        def add_arguments(self, parser):
            parser.add_argument('--pool', default='solo', help='Pool implementation (default: solo)')
            parser.add_argument('--loglevel', default='INFO', help='Logging level (default: INFO)')
            parser.add_argument(
                '--concurrency',
                type=int,
                default=1,
                help='Number of worker processes (default: 1)',
            )
            parser.add_argument(
                '--events',
                '-E',
                action='store_true',
                help='Enable events (default: False)',
            )
            parser.add_argument(
                '--queues',
                '-Q',
                type=str,
                help='List of queues to process (comma separated)',
            )

        def handle(self, *args, **options):
            try:
                self.stdout.write(self.style.SUCCESS('Starting Celery Worker...'))

                # Ensure Celery app is initialized for arbitrary project layout
                resolve_celery_app()

                worker_kwargs = {
                    'pool': options['pool'],
                    'loglevel': options['loglevel'],
                    'concurrency': options['concurrency'],
                    'enable_events': options['events'],
                }

                if options['queues']:
                    worker_kwargs['queues'] = [q.strip() for q in options['queues'].split(',')]
                    self.stdout.write(f'Processing queues: {", ".join(worker_kwargs["queues"])}')

                worker = current_app.Worker(**worker_kwargs)
                worker.start()
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Received stop signal. Shutting down...'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error starting Celery Worker: {e}'))

except ImportError:
    pass
