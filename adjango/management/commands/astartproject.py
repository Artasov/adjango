# management/commands/astartproject.py
"""Create new Django project by cloning adjango-template repository."""

import shutil
import subprocess
from pathlib import Path

from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    """Custom startproject command using remote adjango-template skeleton."""

    help = "Create a new project by cloning https://github.com/Artasov/adjango-template"  # noqa: A003

    REPO_URL = "https://github.com/Artasov/adjango-template"

    def add_arguments(self, parser):
        parser.add_argument(
            "directory",
            nargs="?",
            default=".",
            help="Optional target directory (default: current directory).",
        )

    def handle(self, *args, **options):
        raw_dir = options["directory"]

        # Determine target directory
        if raw_dir in (None, "."):
            target_dir = Path.cwd()
        else:
            given = Path(raw_dir)
            target_dir = (Path.cwd() / given) if not given.is_absolute() else given
        target_dir = target_dir.resolve()

        if target_dir.exists() and any(target_dir.iterdir()):
            raise CommandError(
                f"Directory '{target_dir}' already exists and is not empty"
            )

        target_dir.mkdir(parents=True, exist_ok=True)

        # Clone template
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", self.REPO_URL, str(target_dir)],
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise CommandError(f"Failed to clone repository: {exc}")

        # Remove .git so project starts "from scratch"
        git_dir = target_dir / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir, ignore_errors=True)

        self.stdout.write(self.style.SUCCESS(f"Project created at {target_dir}"))
