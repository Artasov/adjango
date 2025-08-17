# management/commands/astartproject.py
"""Create new Django project by copying base_project template."""

import shutil
from pathlib import Path

from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    """Custom startproject command using pre-defined base_project template."""

    help = "Create a new project by copying base_project skeleton."  # noqa: A003

    def add_arguments(self, parser):
        parser.add_argument(
            'directory',
            nargs='?',
            default='.',
            help='Optional target directory (default: current directory).',
        )

    def handle(self, *args, **options):
        raw_dir = options['directory']

        # Определяем целевую директорию
        if raw_dir in (None, '.'):
            target_dir = Path.cwd()
        else:
            given = Path(raw_dir)
            target_dir = (Path.cwd() / given) if not given.is_absolute() else given
        target_dir = target_dir.resolve()

        if target_dir.exists() and any(target_dir.iterdir()):
            raise CommandError(f"Directory '{target_dir}' already exists and is not empty")

        target_dir.mkdir(parents=True, exist_ok=True)

        # Копируем base_project
        base_project_dir = Path(__file__).resolve().parent.parent.parent / 'base_project'
        if not base_project_dir.exists():
            raise CommandError(f"Base project not found: {base_project_dir}")

        shutil.copytree(base_project_dir, target_dir, dirs_exist_ok=True)

        self.stdout.write(self.style.SUCCESS(f"Project created at {target_dir}"))
