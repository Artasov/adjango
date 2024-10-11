import glob
import os

from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Удаляет все миграции во всех приложениях кроме __init__.py'

    def handle(self, *args, **kwargs):
        apps_prepath = settings.ADJANGO_APPS_PREPATH  # префикс приложений (если используется)
        base_dir = settings.BASE_DIR  # базовая директория проекта

        # Проходим по всем приложениям, указанным в INSTALLED_APPS
        for app in settings.INSTALLED_APPS:
            # Проверяем, что приложение начинается с нужного префикса (если указан)
            if apps_prepath is None or app.startswith(apps_prepath):
                app_path = str(os.path.join(base_dir, app.replace('.', '/')))
                migrations_path = os.path.join(app_path, 'migrations')
                if os.path.exists(migrations_path):
                    # Удаляем все файлы миграций, кроме __init__.py
                    files = glob.glob(os.path.join(migrations_path, '*.py'))
                    for file in files:
                        if os.path.basename(file) != '__init__.py':
                            os.remove(file)
                            self.stdout.write(f'Deleted {file}')

                    # Также удаляем все скомпилированные файлы .pyc
                    pyc_files = glob.glob(os.path.join(migrations_path, '*.pyc'))
                    for file in pyc_files:
                        os.remove(file)
                        self.stdout.write(f'Deleted {file}')

        self.stdout.write('Все файлы миграций были удалены.')
