import os

from django.core.management.base import BaseCommand

from adjango.conf import ADJANGO_BACKENDS_APPS, ADJANGO_FRONTEND_APPS


class Command(BaseCommand):
    """
    Adds a file path comment at the top of each .py and frontend file in the specified app(s).

    @usage:
      python manage.py add_paths [app_name] [--exclude name1 name2 ...] [--path /absolute/path]

    @arg app_name: (optional) Name of the app to process. If not specified, all apps will be processed.
    @arg --exclude: (optional) List of folder or file names to exclude from processing.
                      Defaults to excluding 'migrations' folders and '__init__.py' files.
    @arg --path: (optional) Absolute path to the directory to process. If provided, overrides the default app directories.

    @behavior:
      - Process all backend and frontend apps (with default exclusions):
          python manage.py add_paths

      - Process a specific app (e.g., 'social_oauth'):
          python manage.py add_paths social_oauth

      - Process all apps, excluding additional folders or files:
          python manage.py add_paths --exclude migrations __init__.py tests

      - Process a specific app with specified exclusions:
          python manage.py add_paths social_oauth --exclude migrations __init__.py tests

      - Process a specific directory using an absolute path:
          python manage.py add_paths --path /absolute/path/to/directory

      - Process a specific app within a custom directory:
          python manage.py add_paths social_oauth --path /absolute/path/to/directory
    """

    help = 'Adds a file path comment at the top of .py and frontend files in the specified app(s).'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_name',
            nargs='?',
            default=None,
            help='(Optional) Name of the app to process. If not specified, all apps will be processed.'
        )
        parser.add_argument(
            '--exclude',
            nargs='*',
            default=['migrations', '__init__.py'],
            help="List of folder or file names to exclude. Defaults to 'migrations' and '__init__.py'."
        )
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help="(Optional) Absolute path to the directory to process. Overrides default app directories."
        )

    def handle(self, *args, **options):
        app_name = options['app_name']
        exclude_names = options['exclude']
        custom_path = options['path']

        if custom_path:
            if not os.path.isabs(custom_path):
                self.stderr.write("The --path argument must be an absolute path.")
                return
            if not os.path.exists(custom_path):
                self.stderr.write(f"The specified path '{custom_path}' does not exist.")
                return
            self.stdout.write(f"Processing custom path: '{custom_path}'")
            # Determine file extensions based on directory (assuming backend if processing .py)
            # This can be adjusted as needed
            file_extensions = ('.py', '.ts', '.tsx', '.js', '.jsx')
            self.process_custom_path(custom_path, exclude_names, file_extensions)
        else:
            # Process backend apps
            self.process_apps(app_name, exclude_names, ADJANGO_BACKENDS_APPS, '.py')

            # Process frontend apps
            self.process_apps(app_name, exclude_names, ADJANGO_FRONTEND_APPS, ('.ts', '.tsx', '.js', '.jsx'))

    def process_apps(self, app_name, exclude_names, apps_dir, file_extensions):
        if app_name:
            app_paths = [os.path.join(apps_dir, app_name)]
            if not os.path.exists(app_paths[0]):
                self.stderr.write(f"App '{app_name}' does not exist in the specified directory '{apps_dir}'.")
                return
        else:
            # Process all apps in the directory
            app_paths = [
                os.path.join(apps_dir, name) for name in os.listdir(apps_dir)
                if os.path.isdir(os.path.join(apps_dir, name)) and not name.startswith('__')
            ]

        for app_path in app_paths:
            current_app = os.path.basename(app_path)
            self.stdout.write(f"Processing app '{current_app}'...")
            for root, dirs, files in os.walk(str(app_path)):
                # Exclude specified directories
                dirs[:] = [d for d in dirs if d not in exclude_names]
                for file_name in files:
                    if isinstance(file_extensions, tuple):
                        if not any(file_name.endswith(ext) for ext in file_extensions):
                            continue
                    else:
                        if not file_name.endswith(file_extensions):
                            continue
                    if file_name in exclude_names:
                        continue
                    file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(file_path, apps_dir)
                    self.check_and_fix_file(file_path, relative_path)

    def process_custom_path(self, custom_path, exclude_names, file_extensions):
        for root, dirs, files in os.walk(custom_path):
            # Exclude specified directories
            dirs[:] = [d for d in dirs if d not in exclude_names]
            for file_name in files:
                if isinstance(file_extensions, tuple):
                    if not any(file_name.endswith(ext) for ext in file_extensions):
                        continue
                else:
                    if not file_name.endswith(file_extensions):
                        continue
                if file_name in exclude_names:
                    continue
                file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(file_path, custom_path)
                self.check_and_fix_file(file_path, relative_path)

    def check_and_fix_file(self, file_path, relative_path):
        """
        Checks and updates the file by adding or correcting the file path comment at the top.

        @param file_path: Full path to the file.
        @param relative_path: Relative path of the file from the app's directory or custom path.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (UnicodeDecodeError, FileNotFoundError) as e:
            self.stderr.write(f"Skipping file '{file_path}': {e}")
            return

        # Determine comment style based on file extension
        if file_path.endswith('.py'):
            expected_comment = f'# {relative_path.replace(os.sep, "/")}\n'
        else:
            expected_comment = f'// {relative_path.replace(os.sep, "/")}\n'

        if lines:
            first_line = lines[0].strip()
            if first_line == expected_comment.strip():
                # The file already has the correct comment
                return
            elif first_line.startswith(('#', '//')):
                # The file has a comment, but it's incorrect
                if first_line != expected_comment.strip():
                    # Update the comment
                    lines[0] = expected_comment
                    self.write_file(file_path, lines)
                    self.stdout.write(f"{file_path}: Updated comment")
            else:
                # The first line is not a comment, insert the correct comment at the top
                lines.insert(0, expected_comment)
                self.write_file(file_path, lines)
                self.stdout.write(f"{file_path}: Added missing comment")
        else:
            # File is empty, write the comment
            lines = [expected_comment]
            self.write_file(file_path, lines)
            self.stdout.write(f"{file_path}: Added missing comment to empty file")

    @staticmethod
    def write_file(file_path, lines):
        """
        Writes the updated lines back to the file.

        @param file_path: Full path to the file.
        @param lines: List of lines to write to the file.
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
