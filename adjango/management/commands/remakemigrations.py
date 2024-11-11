# management/commands/remakemigrations.py
from time import sleep

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'Deletes all migration files and then recreates them and applies them.'

    def handle(self, *args, **kwargs):
        # Step 1: Delete all migrations
        self.stdout.write('Deleting migrations...')
        call_command('deletemigrations')  # Use the deletemigrations command
        sleep(1)

        # Step 2: Create new migrations
        self.stdout.write('Creating new migrations...')
        call_command('makemigrations')
        self.stdout.write('Creating migrations completed.')
        sleep(1)

        # Step 3: Apply Migrations
        self.stdout.write('Applying migrations...')
        call_command('migrate')
        self.stdout.write('All migrations applied successfully.')
