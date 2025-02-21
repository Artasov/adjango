# management/commands/copy_from_root.py
import os

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Copies the combined content of all files in the specified directory and its subdirectories to the clipboard.'

    def add_arguments(self, parser):
        parser.add_argument(
            'path',
            type=str,
            help='Absolute path to the directory to process.'
        )

    def handle(self, *args, **options):
        path = options['path']

        # Validate that the path is absolute
        if not os.path.isabs(path):
            raise CommandError('The path argument must be an absolute path.')

        # Validate that the path exists
        if not os.path.exists(path):
            raise CommandError(f"The specified path '{path}' does not exist.")

        # Validate that the path is a directory
        if not os.path.isdir(path):
            raise CommandError(f"The specified path '{path}' is not a directory.")

        self.stdout.write(f"Processing directory: {path}")

        concatenated_text = ""

        # Define excluded directories and files
        excluded_dirs = {
            '__pycache__',
            'node_modules',
            '.git',
            'venv',
            '.env',
            'env',
            'build',
            'dist',
            'migrations',
            'cache',
            'logs',
        }

        excluded_files = {
            '__init__.py',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '*.swp',
            '*.swo',
            'Thumbs.db',
            '.DS_Store',
        }

        # Recursively walk through directories and files
        for root, dirs, files in os.walk(path):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in excluded_dirs]

            for file_name in sorted(files):
                # Skip excluded files
                if self.is_excluded(file_name, excluded_files):
                    self.stdout.write(f"Skipping excluded file: {os.path.join(root, file_name)}")
                    continue

                file_path = str(os.path.join(root, file_name))
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Add header with relative file path
                        relative_path = os.path.relpath(file_path, path)
                        concatenated_text += f"\n--- {relative_path.replace(os.sep, '/')} ---\n"
                        concatenated_text += content + "\n"
                except (UnicodeDecodeError, FileNotFoundError, PermissionError) as e:
                    self.stderr.write(f"Skipping file '{file_path}': {e}")

        if not concatenated_text:
            self.stdout.write(self.style.WARNING("No content to copy."))
            return

        try:
            import pyperclip
        except ImportError:
            pyperclip = None

        if pyperclip is None:
            raise CommandError("The 'pyperclip' module is not installed. Install it using 'pip install pyperclip'.")

        try:
            pyperclip.copy(concatenated_text)
            self.stdout.write(self.style.SUCCESS("Content successfully copied to the clipboard."))
        except pyperclip.PyperclipException as e:
            raise CommandError(f"Failed to copy to clipboard: {e}")

    @staticmethod
    def is_excluded(file_name, excluded_patterns):
        """
        Determines if a file should be excluded based on its name and excluded patterns.

        Args:
            file_name (str): The name of the file.
            excluded_patterns (set): A set of patterns or exact file names to exclude.

        Returns:
            bool: True if the file should be excluded, False otherwise.
        """
        for pattern in excluded_patterns:
            if pattern.startswith('*'):
                if file_name.endswith(pattern[1:]):
                    return True
            elif pattern == file_name:
                return True
        return False
