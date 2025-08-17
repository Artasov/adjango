# management/commands/astartup.py
"""Create an application inside the apps directory with default structure."""

from pathlib import Path

from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    """Create app skeleton in ``apps`` and register it in settings."""  # noqa: A003

    help = "Create app inside apps folder with pre-defined structure."  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument('name', help='Application name')

    def handle(self, *args, **options):
        app_name = options['name']
        base_dir = Path.cwd()
        apps_dir = base_dir / 'apps'
        if not apps_dir.exists():
            raise CommandError('apps directory not found')

        app_dir = apps_dir / app_name
        if app_dir.exists():
            raise CommandError(f"App '{app_name}' already exists")

        # Define required subdirectories and file names
        directories = {
            'controllers': 'base.py',
            'admin': 'base.py',
            'exceptions': 'base.py',
            'models': 'base.py',
            'roads': 'api.py',
            'serializers': 'base.py',
            'services': 'base.py',
            'tests': 'base.py',
        }

        for folder, filename in directories.items():
            path = app_dir / folder
            path.mkdir(parents=True, exist_ok=True)
            (path / '__init__.py').write_text('')
            (path / filename).write_text('')

        (app_dir / '__init__.py').write_text('')

        # Update settings.py to include the new app
        settings_path = base_dir / 'config' / 'settings.py'
        content = settings_path.read_text().splitlines()
        inserted = False
        for i, line in enumerate(content):
            if line.strip().startswith('INSTALLED_APPS') and line.strip().endswith('['):
                content.insert(i + 1, f"    'apps.{app_name}',")
                inserted = True
                break
        if not inserted:
            raise CommandError('INSTALLED_APPS not found in settings.py')

        settings_path.write_text('\n'.join(content) + '\n')

        self.stdout.write(self.style.SUCCESS(f"App '{app_name}' created"))
