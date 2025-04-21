# management/commands/startworker.py
try:
    from celery import current_app
    from django.core.management.base import BaseCommand


    class Command(BaseCommand):
        """
        python manage.py startworker --pool=solo --loglevel=info -E
        """
        help = 'Starts the Celery Worker'

        def add_arguments(self, parser):
            parser.add_argument(
                '--pool',
                default='solo',
                help='Pool implementation (default: solo)'
            )
            parser.add_argument(
                '--loglevel',
                default='INFO',
                help='Log level (default: INFO)'
            )
            parser.add_argument(
                '--concurrency',
                type=int,
                default=1,
                help='Number of worker processes (default: 1)'
            )
            parser.add_argument(
                '--events', '-E',
                action='store_true',
                help='Enable events (default: False)'
            )

        def handle(self, *args, **options):
            worker = current_app.Worker(
                pool=options['pool'],
                loglevel=options['loglevel'],
                concurrency=options['concurrency'],
                enable_events=options['events'],
            )
            worker.start()
except ImportError:
    pass
