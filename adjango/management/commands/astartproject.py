# management/commands/astartproject.py
"""Create new Django project with config package and apps/core structure."""

from pathlib import Path

from django.core.management import BaseCommand, CommandError, call_command


class Command(BaseCommand):
    """Custom startproject command creating config package and default core app."""

    help = "Create a new project with inner 'config' package and default 'core' app."  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument(
            'name',
            help='Name of the project (outer directory).'
        )
        parser.add_argument(
            'directory',
            nargs='?',
            default=None,
            help='Optional target directory.'
        )

    def handle(self, *args, **options):
        project_name = options['name']
        directory = options['directory']

        target_dir = Path(directory or project_name).resolve()
        if target_dir.exists():
            raise CommandError(f"Directory '{target_dir}' already exists")

        target_dir.mkdir(parents=True)

        # Use Django's startproject to create base structure with inner package 'config'.
        call_command('startproject', 'config', str(target_dir))

        apps_dir = target_dir / 'apps'
        core_dir = apps_dir / 'core'
        roads_dir = core_dir / 'roads'

        # Create apps/core/roads structure
        roads_dir.mkdir(parents=True)
        (apps_dir / '__init__.py').write_text('')
        (core_dir / '__init__.py').write_text('')
        (roads_dir / '__init__.py').write_text('')
        (roads_dir / 'root.py').write_text(
            'from django.urls import path\n\nurlpatterns = []\n'
        )

        # Adjust settings
        settings_path = target_dir / 'config' / 'settings.py'
        content = settings_path.read_text().splitlines()

        # Insert apps.core into INSTALLED_APPS
        for i, line in enumerate(content):
            if line.strip().startswith('INSTALLED_APPS') and line.strip().endswith('['):
                content.insert(i + 1, "    'apps.core',")
                break
        else:  # pragma: no cover - default startproject always has INSTALLED_APPS
            raise CommandError('INSTALLED_APPS not found in settings.py')

        # Set ROOT_URLCONF to core roads
        replaced = False
        for i, line in enumerate(content):
            if line.strip().startswith('ROOT_URLCONF'):
                content[i] = "ROOT_URLCONF = 'apps.core.roads.root'"
                replaced = True
                break
        if not replaced:
            content.append("ROOT_URLCONF = 'apps.core.roads.root'")

        settings_path.write_text('\n'.join(content) + '\n')

        # Remove default urls.py as routes are stored in core roads
        default_urls = target_dir / 'config' / 'urls.py'
        if default_urls.exists():
            default_urls.unlink()

        self.stdout.write(self.style.SUCCESS(f"Project created at {target_dir}"))
