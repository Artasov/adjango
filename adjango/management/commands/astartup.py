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

        # Ensure apps/ exists
        apps_dir = base_dir / 'apps'
        apps_dir.mkdir(parents=True, exist_ok=True)

        app_dir = apps_dir / app_name
        if app_dir.exists():
            raise CommandError(f"App '{app_name}' already exists")

        # Define required subdirectories and file names (no routes here; astartproject will add routes/root.py)
        directories = {
            'controllers': 'base.py',
            'admin': 'base.py',
            'exceptions': 'base.py',
            'models': 'base.py',
            'serializers': 'base.py',
            'services': 'base.py',
            'tests': 'base.py',
        }

        for folder, filename in directories.items():
            path = app_dir / folder
            path.mkdir(parents=True, exist_ok=True)
            (path / '__init__.py').write_text('', encoding='utf-8')
            (path / filename).write_text('', encoding='utf-8')

        (app_dir / '__init__.py').write_text('', encoding='utf-8')

        # Update settings.py to include the new app
        settings_path = base_dir / 'config' / 'settings.py'
        if not settings_path.exists():
            raise CommandError('settings.py not found at config/settings.py')

        content = settings_path.read_text(encoding='utf-8').splitlines()

        inserted = False
        for i, line in enumerate(content):
            stripped = line.strip()
            # Default Django: "INSTALLED_APPS = ["
            if stripped.startswith('INSTALLED_APPS') and stripped.endswith('['):
                content.insert(i + 1, f"    'apps.{app_name}',")
                inserted = True
                break

        if not inserted:
            # Fallback: try to find a line that is exactly the opening bracket on the next line
            try:
                idx = next(
                    i for i, ln in enumerate(content)
                    if ln.strip() == 'INSTALLED_APPS = [' or ln.strip() == 'INSTALLED_APPS=['
                )
                content.insert(idx + 1, f"    'apps.{app_name}',")
                inserted = True
            except StopIteration:
                pass

        if not inserted:
            raise CommandError('INSTALLED_APPS not found in settings.py')

        settings_path.write_text('\n'.join(content) + '\n', encoding='utf-8')

        self.stdout.write(self.style.SUCCESS(f"App '{app_name}' created"))
