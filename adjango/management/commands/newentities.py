# management/commands/newentities.py
"""Generate entity skeletons (exceptions/models/services/serializers/tests) for an app."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, List, Optional

from django.core.management import BaseCommand, CommandError, call_command
from django.core.management.base import CommandParser


def camel_to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


class Command(BaseCommand):
    """Create entities in the target app with module subfolders."""

    help = (
        "Usage:\n"
        "  python manage.py newentities <module> <app_label> <Model1,Model2,...>\n\n"
        "Examples:\n"
        "  python manage.py newentities order apps.commerce Order,Product,Price\n"
        "  python manage.py newentities order apps.commerce Order\n"
    )  # noqa: A003

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("module", help="Module name (e.g., order)")
        parser.add_argument(
            "app_label", help="App label in dotted path (e.g., apps.commerce)"
        )
        parser.add_argument(
            "models_csv", help="Comma-separated model names (e.g., Order,Product,Price)"
        )

    def handle(self, *args: Any, **options: Any) -> None:
        module: str = options["module"].strip()
        app_label: str = options["app_label"].strip()
        models_csv: str = options["models_csv"].strip()

        if not module or not app_label or not models_csv:
            raise CommandError("module, app_label and models_csv are required")

        model_names: List[str] = [m.strip() for m in models_csv.split(",") if m.strip()]
        if not model_names:
            raise CommandError("Provide at least one model in models_csv")

        base_dir = Path.cwd()
        apps_dir = base_dir / "apps"
        if not apps_dir.exists():
            raise CommandError("`apps` directory not found in current project root")

        # Parse app_label like "apps.commerce"
        parts = app_label.split(".")
        if len(parts) < 2 or parts[0] != "apps":
            raise CommandError("app_label must start with 'apps.', e.g. apps.commerce")

        app_name = parts[1]
        app_dir = apps_dir / app_name

        # If app doesn't exist - create it via astartup
        if not app_dir.exists():
            call_command("astartup", app_name)

        # Check that it actually exists after creation
        if not app_dir.exists():
            raise CommandError(f"App '{app_label}' was not created")

        # Prepare paths
        exceptions_dir = app_dir / "exceptions"
        models_dir = app_dir / "models"
        services_dir = app_dir / "services"
        serializers_dir = app_dir / "serializers"
        tests_dir = app_dir / "tests"

        for d in (exceptions_dir, models_dir, services_dir, serializers_dir, tests_dir):
            d.mkdir(parents=True, exist_ok=True)
            (d / "__init__.py").touch()

        # If single model - place files directly (without subfolders) with module.py name
        single_model = len(model_names) == 1

        if single_model:
            model = model_names[0]
            model_snake = camel_to_snake(model)

            # exceptions/<module>.py (empty)
            (exceptions_dir / f"{module}.py").touch()

            # services/<module>.py
            (services_dir / f"{module}.py").write_text(
                self._render_service(app_label, module, model, model_snake),
                encoding="utf-8",
            )

            # models/<module>.py
            (models_dir / f"{module}.py").write_text(
                self._render_model(app_label, module, model, model_snake, single=True),
                encoding="utf-8",
            )

            # serializers/<module>.py
            (serializers_dir / f"{module}.py").write_text(
                self._render_serializer_stub(app_label, module, [model]),
                encoding="utf-8",
            )

            # tests/<module>.py
            (tests_dir / f"{module}.py").write_text(
                self._render_tests_stub(app_label, module, [model]),
                encoding="utf-8",
            )

            # Update models/__init__.py (from .<module> import Model)
            self._update_models_init(models_dir, imports=[(module, model)])

        else:
            # Multiple models - create <module>/ subfolders and files per model
            for base in (
                exceptions_dir,
                services_dir,
                serializers_dir,
                tests_dir,
                models_dir,
            ):
                (base / module).mkdir(parents=True, exist_ok=True)
                ((base / module) / "__init__.py").touch()

            # exceptions/<module>/<model>.py (empty)
            for model in model_names:
                ((exceptions_dir / module) / f"{camel_to_snake(model)}.py").touch()

            # services/<module>/<model>.py
            for model in model_names:
                model_snake = camel_to_snake(model)
                ((services_dir / module) / f"{model_snake}.py").write_text(
                    self._render_service(app_label, module, model, model_snake),
                    encoding="utf-8",
                )

            # models/<module>/<model>.py
            for model in model_names:
                model_snake = camel_to_snake(model)
                ((models_dir / module) / f"{model_snake}.py").write_text(
                    self._render_model(
                        app_label, module, model, model_snake, single=False
                    ),
                    encoding="utf-8",
                )

            # serializers/<module>/<model>.py
            for model in model_names:
                model_snake = camel_to_snake(model)
                ((serializers_dir / module) / f"{model_snake}.py").write_text(
                    self._render_serializer_stub(app_label, module, [model]),
                    encoding="utf-8",
                )

            # tests/<module>/<model>.py
            for model in model_names:
                model_snake = camel_to_snake(model)
                ((tests_dir / module) / f"{model_snake}.py").write_text(
                    self._render_tests_stub(app_label, module, [model]),
                    encoding="utf-8",
                )

            # Update models/<module>/__init__.py and root models/__init__.py
            subpkg_init_imports = [
                (f"{module}.{camel_to_snake(m)}", m) for m in model_names
            ]
            self._update_models_init(
                models_dir, subpkg_module=module, imports=subpkg_init_imports
            )
            self._update_models_init(
                models_dir,
                imports=[(f"{module}.{camel_to_snake(m)}", m) for m in model_names],
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Entities created for {app_label}:{module} → {', '.join(model_names)}"
            )
        )

    # ---------- render helpers ----------

    def _render_service(
        self, app_label: str, module: str, model: str, model_snake: str
    ) -> str:
        return f"""from __future__ import annotations

from typing import TYPE_CHECKING

from adjango.services.base import ABaseService


if TYPE_CHECKING:
    from {app_label}.models import {model}


class {model}Service(ABaseService):
    def __init__(self, {model_snake}: '{model}') -> None:
        super().__init__({model_snake})
        self.{model_snake} = {model_snake}
"""

    def _render_model(
        self, app_label: str, module: str, model: str, model_snake: str, single: bool
    ) -> str:
        # Path to service
        if single:
            service_import = f"from {app_label}.services.{module} import {model}Service"
        else:
            service_import = f"from {app_label}.services.{module}.{model_snake} import {model}Service"

        return f"""from __future__ import annotations

from adjango.models import AModel
from django.utils.translation import gettext_lazy as _

{service_import}


class {model}(AModel):
    # TODO: add fields

    class Meta:
        verbose_name = _('{model}')
        verbose_name_plural = _('{model}s')

    def __str__(self): return f'{{self.__class__.__name__}} #{{self.id}}'

    @property
    def service(self) -> {model}Service:
        return {model}Service(self)
"""

    def _render_serializer_stub(
        self, app_label: str, module: str, models: List[str]
    ) -> str:
        # Simple stub
        lines = [
            "from adjango.aserializers import AModelSerializer",
            "",
        ]
        for m in models:
            lines.append(f"from {app_label}.models import {m}")
        lines.append("")
        lines.append("")
        for m in models:
            lines.append(f"class {m}Serializer(AModelSerializer):")
            lines.append("    class Meta:")
            lines.append(f"        model = {m}")
            lines.append("        fields = '__all__'")
            lines.append("")
        return "\n".join(lines)

    def _render_tests_stub(self, app_label: str, module: str, models: List[str]) -> str:
        return ""

    # ---------- __init__ updaters ----------

    def _update_models_init(
        self,
        models_dir: Path,
        imports: List[tuple[str, str]],
        subpkg_module: Optional[str] = None,
    ) -> None:
        """
        Add imports to models/__init__.py (and if needed to models/<module>/__init__.py).

        imports: list of (module_path_tail, ClassName)
            - if subpkg_module is None: module_path_tail can be 'order' (single) or 'order.order' (multi)
            - if subpkg_module is not None: this will update __init__ inside subpackage.
        """
        if subpkg_module:
            init_path = models_dir / subpkg_module / "__init__.py"
        else:
            init_path = models_dir / "__init__.py"

        init_path.parent.mkdir(parents=True, exist_ok=True)
        if not init_path.exists():
            init_path.write_text("", encoding="utf-8")

        existing = init_path.read_text(encoding="utf-8").splitlines()
        existing_text = "\n".join(existing)

        new_lines: List[str] = []
        all_names: List[str] = []

        # Preserve existing lines and collect already declared __all__
        existing_all: List[str] = []
        for line in existing:
            new_lines.append(line)
            if line.startswith("__all__"):
                # rough parser for existing __all__
                m = re.search(r"__all__\s*=\s*\[([^\]]*)\]", line)
                if m:
                    names = [
                        x.strip().strip("'\"")
                        for x in m.group(1).split(",")
                        if x.strip()
                    ]
                    existing_all.extend(names)

        # Add imports if they don't exist
        for mod_tail, cls in imports:
            import_stmt = f"from .{mod_tail} import {cls}"
            if import_stmt not in existing_text:
                new_lines.append(import_stmt)
            all_names.append(cls)

        # Update __all__
        final_all = list(
            dict.fromkeys(existing_all + all_names)
        )  # preserve order, dedupe
        new_lines = [ln for ln in new_lines if not ln.startswith("__all__")]
        new_lines.append(f"__all__ = [{', '.join([repr(x) for x in final_all])}]")
        new_content = "\n".join(new_lines).rstrip() + "\n"
        init_path.write_text(new_content, encoding="utf-8")
