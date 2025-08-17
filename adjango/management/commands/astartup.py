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

        # Define required subdirectories and file names (no routes here)
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

        # Possible config files where INSTALLED_APPS may reside
        candidate_paths = [
            base_dir / 'config' / 'settings.py',
            base_dir / 'config' / 'modules' / 'apps.py',
        ]

        updated = False
        for settings_path in candidate_paths:
            if not settings_path.exists():
                continue

            content = settings_path.read_text(encoding='utf-8').splitlines()
            new_content = []
            inside_apps = False
            added = False

            for line in content:
                stripped = line.strip()

                if stripped.startswith('INSTALLED_APPS') and stripped.endswith('['):
                    inside_apps = True
                    new_content.append(line)
                    continue

                if inside_apps and stripped.startswith(']') and not added:
                    new_content.append(f"    'apps.{app_name}',")
                    added = True
                    inside_apps = False
                    new_content.append(line)
                    continue

                new_content.append(line)

            if added:
                settings_path.write_text('\n'.join(new_content) + '\n', encoding='utf-8')
                updated = True
                break

        if not updated:
            raise CommandError('INSTALLED_APPS not found in config/settings.py or config/modules/apps.py')

        self.stdout.write(self.style.SUCCESS(f"App '{app_name}' created"))
