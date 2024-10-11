import os

import pyperclip
from django.conf import settings
from django.core.management.base import BaseCommand

TARGET_ALL = [
    'controllers',
    'serializers',
    # 'exceptions',
    'tests',
    'models',
    'routes',
    'classes',
    'urls',
    'service',
    'services',
    # 'decorators',
    # 'permissions',
    # 'tasks',
    # 'middleware',
    # 'forms',
    # 'components',
    # 'pages',
]


class Command(BaseCommand):
    """
    @behavior:
        Handles copying the project structure and
        contents of specified files and directories.
    @usage:
        manage.py copy_proj [target_names] --apps [apps] [-b/--backend] [-f/--frontend]
    @flags:
        -b, --backend: Include backend files.
        -f, --frontend: Include frontend files.
    @args:
        target_names: list of target directory/file names to collect. Defaults to all if not provided.
        backend: flag to include backend files.
        frontend: flag to include frontend files.
        apps: list of app names to collect from. Defaults to all if not provided.
    @raise CommandError:
        If a specified app doesn't exist in backend/frontend.
    """

    help = 'Copy project structure and contents of specific files and directories.'

    IGNORE_FILES = ['__init__.py']

    def add_arguments(self, parser):
        parser.add_argument(
            'target_names', nargs='*', type=str,
            help='List of target names to collect. Defaults to all if not provided.'
        )
        parser.add_argument(
            '--apps', nargs='+', type=str,
            help='List of apps to collect from. Defaults to all if not provided.'
        )
        parser.add_argument(
            '-b', '--backend', action='store_true',
            help='Include backend files.'
        )
        parser.add_argument(
            '-f', '--frontend', action='store_true',
            help='Include frontend files.'
        )

    def handle(self, *args, **options):
        target_names = options['target_names']
        include_backend = options['backend']
        include_frontend = options['frontend']

        # Если флаги не указаны, по умолчанию копируем только backend
        if not include_backend and not include_frontend:
            include_backend = True

        if not target_names or target_names[0] == 'all':
            target_names = TARGET_ALL

        apps_to_include = options['apps'] or self.get_all_apps()

        result = []
        collected_files = {name: [] for name in target_names}

        if include_backend:
            for app in apps_to_include:
                app_path = os.path.join(settings.ADJANGO_APPS_PREPATH, app)
                if not os.path.exists(app_path):
                    self.stdout.write(self.style.ERROR(f"App {app} does not exist in backend. Skipping."))
                    continue
                for root, dirs, files in os.walk(app_path):
                    for name in target_names:
                        if name in dirs:
                            dir_path = os.path.join(root, name)
                            self.collect_directory_contents(dir_path, collected_files[name], settings.BASE_DIR)
                        if name + '.py' in files:
                            file_path = os.path.join(root, name + '.py')
                            self.collect_file_contents(file_path, collected_files[name], settings.BASE_DIR)

        if include_frontend:
            for app in apps_to_include:
                app_path = os.path.join(settings.ADJANGO_FRONTEND_DIR, app)
                if not os.path.exists(app_path):
                    self.stdout.write(self.style.ERROR(f"App {app} does not exist in frontend. Skipping."))
                    continue
                for root, dirs, files in os.walk(app_path):
                    for name in target_names:
                        if name in dirs:
                            dir_path = os.path.join(root, name)
                            self.collect_directory_contents(dir_path, collected_files[name], settings.FRONTEND_DIR)
                        # Проверяем файлы с расширениями фронтенда
                        for ext in ['.ts', '.tsx', '.js', '.jsx']:
                            file_name = name + ext
                            if file_name in files:
                                file_path = os.path.join(root, file_name)
                                self.collect_file_contents(file_path, collected_files[name], settings.FRONTEND_DIR)

        for name in target_names:
            if collected_files[name]:
                result.append(f'\n# {name.capitalize()}\n')
                result.extend(collected_files[name])

        final_text = '\n'.join(result)
        pyperclip.copy(final_text)
        self.stdout.write(self.style.SUCCESS('Project structure and contents copied to clipboard.'))
        print(final_text)

    def collect_directory_contents(self, dir_path, result, base_dir):
        for sub_root, sub_dirs, sub_files in os.walk(dir_path):
            for file in sub_files:
                if (file.endswith('.py') or file.endswith('.ts') or file.endswith('.tsx') or file.endswith(
                        '.js') or file.endswith('.jsx')) and file not in self.IGNORE_FILES:
                    file_path = os.path.join(sub_root, file)
                    self.collect_file_contents(file_path, result, base_dir)

    @staticmethod
    def collect_file_contents(file_path, result, base_dir):
        relative_path = os.path.relpath(file_path, base_dir)
        result.append(f'\n# {relative_path}\n')
        with open(file_path, 'r', encoding='utf-8') as f:
            result.append(f.read())

    @staticmethod
    def get_all_apps():
        apps_path = os.path.join(settings.ADJANGO_BACKENDS_APPS)
        return [name for name in os.listdir(apps_path) if os.path.isdir(os.path.join(apps_path, name))]
