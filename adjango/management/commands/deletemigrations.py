# management/commands/deletemigrations.py
import glob
import os

from django.conf import settings
from django.core.management import BaseCommand

from adjango.conf import ADJANGO_APPS_PREPATH


class Command(BaseCommand):
    help = "Deletes all migrations in all applications except __init__.py"

    def handle(self, *args, **kwargs):
        apps_prepath = ADJANGO_APPS_PREPATH  # app prefix (if used)
        base_dir = settings.BASE_DIR  # project base directory

        # Go through all applications specified in INSTALLED_APPS
        for app in settings.INSTALLED_APPS:
            # Check that application starts with required prefix (if specified)
            if apps_prepath is None or app.startswith(apps_prepath):
                app_path = str(os.path.join(base_dir, app.replace(".", "/")))
                migrations_path = os.path.join(app_path, "migrations")
                if os.path.exists(migrations_path):
                    # Delete all migration files except __init__.py
                    files = glob.glob(os.path.join(migrations_path, "*.py"))
                    for file in files:
                        if os.path.basename(file) != "__init__.py":
                            os.remove(file)
                            self.stdout.write(f"Deleted {file}")

                    # Also delete all compiled .pyc files
                    pyc_files = glob.glob(os.path.join(migrations_path, "*.pyc"))
                    for file in pyc_files:
                        os.remove(file)
                        self.stdout.write(f"Deleted {file}")

        self.stdout.write("All migration files have been deleted.")
