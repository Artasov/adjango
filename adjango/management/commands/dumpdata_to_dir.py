# management/commands/dumpdata_to_dir.py
import os
from typing import Any

from django.apps import apps
from django.core.management import BaseCommand, call_command
from django.core.management.base import CommandError


class Command(BaseCommand):
    """
    Dumps data from all models into separate JSON files within a specified directory.

    Usage: python manage.py <command> <directory>
    """

    help = "Dumps data from all models into separate files within a specified directory"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "directory", type=str, help="Directory where data files will be saved"
        )

    def handle(self, *args: tuple, **options: Any) -> None:
        directory = options["directory"]
        if not os.path.exists(directory):
            os.makedirs(directory)

        for app in apps.get_app_configs():
            for model in app.get_models():
                app_label = app.label
                model_name = model.__name__
                model_label = f"{app_label}_{model_name}"
                output_file_path = os.path.join(directory, f"{model_label}.json")
                self.stdout.write(
                    f"Dumping data for {model_label} into {output_file_path}"
                )
                try:
                    with open(output_file_path, "w", encoding="utf-8") as output_file:
                        call_command(
                            "dumpdata", f"{app_label}.{model_name}", stdout=output_file
                        )
                except (OSError, CommandError) as e:
                    self.stderr.write(f"Failed to dump {model_name}: {e}")
