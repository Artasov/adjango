"""
Django management command to copy project objects based on a configuration file.

This command reads a configuration file specified in settings.COPY_PROJECT_CONFIGURATIONS,
which must define a variable called 'configurations'. Each configuration is a nested dictionary
that defines what objects (files, folders, classes, functions, etc.) to copy from the project.
It recursively processes the configuration, resolves dotted paths to source code, and collects
the source code of the specified objects.

Special keys in the configuration:
  - __exclude__: A list of substrings; if any substring is found in a file or folder name, that item is skipped.
  - __add_paths__: If True, a comment containing the relative path from BASE_DIR is added at the beginning
                   of each copied source. The comment style is determined by the file extension.

Example configuration in settings.COPY_PROJECT_CONFIGURATIONS = BASE_DIR / copy_conf.py:

    configurations = {
        'base': {
            '__exclude__': [
                '__init__',
                'pycache',
                '.pyc',
            ],
            '__add_paths__': True,
            'apps.core.routes.root': '__copy__',
            'apps.core.models': {
                'user': '__copy__'
            },
            'apps.psychology': {
                'models': {
                    'consultation': {
                        'Consultation': '__copy__',
                        'ConsultationDuration': '__copy__',
                    },
                    'psychologist': '__copy__'
                }
            },
            'apps.commerce': {
                'models': {
                    'order': '__copy__',
                    'product': '__copy__',
                    'promocode': '__copy__',
                },
                'serializers': {
                    'order': '__copy__',
                    'product': '__copy__',
                    'promocode': '__copy__',
                }
            },
        },
        'config_v_2': {
            # additional configuration settings...
        }
    }

By default, if no configuration name is provided when running the command,
the 'base' configuration is used.

Usage:
    python manage.py copy_project [conf_name] [--output output_file]

If --output is specified, the collected source code is written to the given file.
Otherwise, if the pyperclip module is installed, the result is copied to the clipboard.
"""

import importlib
import importlib.util
import inspect
import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Copies project objects based on the configuration (files, folders, classes, functions) with additional options.'

    def add_arguments(self, parser):
        parser.add_argument('conf_name', nargs='?', default='base', type=str,
                            help='Configuration name from copy_conf.py (default: base)')
        parser.add_argument(
            '--output',
            type=str,
            help='Path to the output file. If not specified, the result is copied to the clipboard.',
            default=None
        )

    def handle(self, *args, **options):
        conf_name = options['conf_name']
        output_file = options['output']

        # Load the configuration file specified in settings.COPY_PROJECT_CONFIGURATIONS
        copy_conf_path = settings.COPY_PROJECT_CONFIGURATIONS
        if not os.path.exists(copy_conf_path):
            self.stderr.write(self._color_text(f'Configuration file not found: {copy_conf_path}', 'red'))
            sys.exit(1)
        spec = importlib.util.spec_from_file_location('copy_conf', str(copy_conf_path))
        copy_conf = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(copy_conf)

        if not hasattr(copy_conf, 'configurations'):
            self.stderr.write(
                self._color_text('The configuration file does not contain the \'configurations\' variable', 'red'))
            sys.exit(1)

        configurations = copy_conf.configurations
        if conf_name not in configurations:
            self.stderr.write(self._color_text(f'Configuration \'{conf_name}\' not found', 'red'))
            sys.exit(1)

        config = configurations[conf_name]
        collected_sources = []

        # Extract base options from configuration (if provided)
        base_options = {
            'exclude': config.get('__exclude__', []),
            'add_paths': config.get('__add_paths__', False),
        }

        def process_path(prefix, conf_item, opts):  # 'opts' now used instead of 'options'
            """
            Recursively traverses the configuration.
            If the value is '__copy__', attempts to retrieve the source code for the object at the given dotted path.
            If the value is a dictionary, updates local options and recursively processes its keys.
            """
            if isinstance(conf_item, dict):
                # Update options for the current level (inherit parent options)
                local_options = opts.copy()
                # Update special keys if defined at this level
                for special in ['__exclude__', '__add_paths__']:
                    if special in conf_item:
                        if special == '__exclude__':
                            local_options['exclude'] = conf_item[special]
                        elif special == '__add_paths__':
                            local_options['add_paths'] = conf_item[special]
                # Process all keys that do not start with '__'
                for key, value in conf_item.items():
                    if key.startswith('__'):
                        continue
                    new_prefix = f'{prefix}.{key}' if prefix else key
                    process_path(new_prefix, value, local_options)
            elif isinstance(conf_item, str):
                if conf_item == '__copy__':
                    try:
                        source = self.resolve_source(prefix, opts)
                        collected_sources.append(source)
                        self.stdout.write(self._color_text(f'Copied: {prefix}', 'green'))
                    except Exception as er:
                        self.stderr.write(self._color_text(f'Not found: {prefix} ({str(er)})', 'red'))
                else:
                    self.stderr.write(self._color_text(f'Unknown directive \'{conf_item}\' for {prefix}', 'red'))
            else:
                self.stderr.write(self._color_text(f'Invalid configuration for {prefix}', 'red'))

        process_path('', config, base_options)

        final_text = '\n\n'.join(collected_sources)
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(final_text)
                self.stdout.write(self._color_text(f'Result saved to file: {output_file}', 'green'))
            except Exception as e:
                self.stderr.write(self._color_text(f'Error writing to file {output_file}: {str(e)}', 'red'))
        else:
            # Optionally: if you want to copy to the clipboard, install pyperclip (pip install pyperclip)
            try:
                import pyperclip
            except ImportError:
                pyperclip = None
            if pyperclip:
                pyperclip.copy(final_text)
                self.stdout.write(self._color_text('Result copied to clipboard', 'green'))
            else:
                self.stderr.write(
                    self._color_text('pyperclip module is not installed. Could not copy to clipboard.', 'red'))

    def resolve_source(self, dotted_path, options):
        """
        Attempts to retrieve the source code for an object using its dotted path.
        If the module or object is imported successfully, returns its source code.
        If the object is a package (has an __init__.py), copies all files in the folder with the given options.
        If importing fails, tries to locate a file with one of several extensions.
        If the add_paths option is enabled, a comment with the file path is added to the source.
        """
        try:
            module = importlib.import_module(dotted_path)
            file_path = getattr(module, '__file__', None)
            if file_path and os.path.basename(file_path) == '__init__.py':
                # This is a package - copy the entire folder
                source = self.copy_folder(os.path.dirname(file_path), options)
            else:
                source = inspect.getsource(module)
                file_path = getattr(module, '__file__', None)
            if options.get('add_paths') and file_path:
                source = self.add_path_comment(source, file_path)
            return source
        except ModuleNotFoundError:
            # Attempt to get an attribute from the module
            parts = dotted_path.split('.')
            module_path = '.'.join(parts[:-1])
            attr_name = parts[-1]
            if module_path:
                module = importlib.import_module(module_path)
                obj = getattr(module, attr_name)
                file_path = inspect.getsourcefile(obj)
                source = inspect.getsource(obj)
                if options.get('add_paths') and file_path:
                    source = self.add_path_comment(source, file_path)
                return source
            else:
                raise Exception('Failed to resolve path')
        except Exception as e:
            # If importing fails, try to find a file with various extensions
            parts = dotted_path.split('.')
            possible_extensions = ['.py', '.html', '.js', '.css']
            for ext in possible_extensions:
                possible_path = os.path.join(*parts) + ext
                if os.path.exists(possible_path):
                    file_path = possible_path
                    with open(possible_path, encoding='utf-8') as f:
                        source = f.read()
                    if options.get('add_paths') and file_path:
                        source = self.add_path_comment(source, file_path)
                    return source
            raise e

    def copy_folder(self, folder_path, options):
        """
        Recursively traverses the folder and collects source code from all files that meet the conditions.
        Files and folders whose names contain any substring from options['exclude'] are skipped.
        For each file, if the add_paths option is enabled, a comment with the relative path is added.
        """
        collected = []
        for root, dirs, files in os.walk(folder_path):
            # Exclude directories matching any of the patterns
            dirs[:] = [d for d in dirs if not any(excl in d for excl in options.get('exclude', []))]
            for file in files:
                if any(excl in file for excl in options.get('exclude', [])):
                    continue
                file_full = os.path.join(root, file)
                with open(file_full, encoding='utf-8') as f:
                    content = f.read()
                if options.get('add_paths'):
                    content = self.add_path_comment(content, file_full)
                collected.append(content)
        return '\n\n'.join(collected)

    @staticmethod
    def add_path_comment(source, file_path):
        """
        Adds a comment with the relative path from BASE_DIR to the beginning of the source code.
        If the source code already begins with a comment (containing at least one '/'),
        that line is removed before inserting the new comment.
        The comment style is chosen based on the file extension, using forward slashes.
        """
        # Compute the relative path and replace backslashes with forward slashes
        rel_path = os.path.relpath(file_path, settings.BASE_DIR).replace('\\', '/')

        # Choose the comment style based on the file extension; for Python, use '#'
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.py':
            new_comment = f'# {rel_path}\n'
        elif ext == '.js':
            new_comment = f'// {rel_path}\n'
        elif ext == '.html':
            new_comment = f'<!-- {rel_path} -->\n'
        elif ext == '.css':
            new_comment = f'/* {rel_path} */\n'
        else:
            new_comment = f'# {rel_path}\n'

        # Split the source code into lines and check the first line
        lines = source.splitlines()
        if lines:
            first_line = lines[0].strip()
            # If the first line starts with one of the known comment markers and contains '/'
            if first_line.startswith(('#', '//', '/*', '<!--', '/')) and '/' in first_line:
                # Remove the first line
                lines = lines[1:]
                source = '\n'.join(lines)

        # Return the new comment followed by the source code (with the old comment removed if it existed)
        return new_comment + source

    @staticmethod
    def _color_text(text, color):
        colors = {
            'red': '\033[31m',
            'green': '\033[32m',
            'reset': '\033[0m'
        }
        return f'{colors.get(color, "")}{text}{colors["reset"]}'
