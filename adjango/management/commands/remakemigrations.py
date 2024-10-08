# core/management/commands/remakemigrations.py
import glob
import os
from time import sleep

from django.conf import settings
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = ('Delete all migration files from apps in the "apps." namespace, '
            'delete SQLite database file if used, and run makemigrations and migrate')

    def handle(self, *args, **kwargs):
        apps_prepath = settings.ADJANGO_APPS_PREPATH
        base_dir = settings.BASE_DIR

        # Delete migration files
        for app in settings.INSTALLED_APPS:
            if apps_prepath is None or app.startswith(apps_prepath):
                app_path = os.path.join(base_dir, app.replace('.', '/'))
                migrations_path = os.path.join(app_path, 'migrations')
                if os.path.exists(migrations_path):
                    files = glob.glob(os.path.join(migrations_path, '*.py'))
                    for file in files:
                        if os.path.basename(file) != '__init__.py':
                            os.remove(file)
                            self.stdout.write(f'Deleted {file}')

                    pyc_files = glob.glob(os.path.join(migrations_path, '*.pyc'))
                    for file in pyc_files:
                        os.remove(file)
                        self.stdout.write(f'Deleted {file}')

        self.stdout.write('All migration files in apps.* deleted')
        sleep(1)

        # Run makemigrations
        self.stdout.write('Running makemigrations...')
        call_command('makemigrations')
        self.stdout.write('Makemigrations completed')
        sleep(1)
