# management/commands/autosucreate.py
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a superpower if it does not exist yet. Takes the arguments -u (username) and -p (password). By default: username = 123, password = 123.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-u', '--username',
            type=str,
            help='Username',
            default='123'
        )
        parser.add_argument(
            '-p', '--password',
            type=str,
            help='Password',
            default='123'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        User = get_user_model()

        if User.objects.filter(is_staff=True).exists():
            self.stdout.write(self.style.WARNING(f'The superuser already exists, skipping the auto-creation ...'))
        else:
            User.objects.create_superuser(username=username, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" successfully created.'))
