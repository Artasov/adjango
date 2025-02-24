'''
Django management command to copy project objects (files, directories) based on a configuration file.

This command reads a configuration file specified in settings.COPY_PROJECT_CONFIGURATIONS,
which must define a variable called 'configurations'. Each configuration is a nested dictionary
that defines what objects to copy from the project, treating them strictly as files and folders.

Special configuration keys:
  - __start_dir__: The base directory from which all dotted paths will be resolved. Defaults to settings.BASE_DIR if not provided.
  - __exclude__: A list of substrings; if any substring is found in a file or folder name, that item is skipped.
  - __add_paths__: If True, a comment containing the relative path from __start_dir__ is added at the beginning
                   of each copied source. The comment style is determined by the file extension.

Rules:
  - Keys that do not begin with '__' represent dotted paths. The command joins those parts
    via os.path.join(*path.split('.')) relative to __start_dir__.
  - If the value is '__copy__', the command copies the entire directory (if the resolved path is a directory)
    or a single file (if the resolved path is a file), respecting exclusions.
    If the path doesn't exist as-is, it tries a list of known extensions (py, js, jsx, tsx, html, css, etc.).
  - If the value is a nested dictionary, the command descends into that path (which must be a directory) and
    processes its sub-keys accordingly.
  - If the path does not exist even after checking possible extensions, an error is displayed in red.

Example configuration in settings.COPY_PROJECT_CONFIGURATIONS = BASE_DIR / 'copy_conf.py':

    configurations = {
        'base': {
            '__start_dir__': BASE_DIR,  # optional, defaults to BASE_DIR if not specified
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
'''

import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Copies project objects (files, directories) based on a configuration with additional options.'

    # You can adjust this list to include whatever file extensions your frontend/backend uses.
    KNOWN_EXTENSIONS = [
        '.py', '.js', '.jsx', '.tsx', '.ts', '.html', '.css'
        '.yml', '.md', '.txt', '.cfg', '.gitignore', '.po', '.conf'
    ]

    def add_arguments(self, parser):
        parser.add_argument('conf_name', nargs='?', default='base', type=str,
                            help='Configuration name from the config file (default: base)')
        parser.add_argument(
            '--output',
            type=str,
            help='Path to the output file. If not specified, the result is copied to the clipboard.',
            default=None
        )

    def handle(self, *args, **options):
        conf_name = options['conf_name']
        output_file = options['output']

        copy_conf_path = settings.COPY_PROJECT_CONFIGURATIONS
        if not os.path.exists(copy_conf_path):
            self.stderr.write(self._color_text(f'Configuration file not found: {copy_conf_path}', 'red'))
            sys.exit(1)

        # Dynamically import the configuration module
        import importlib.util
        spec = importlib.util.spec_from_file_location('copy_conf', str(copy_conf_path))
        copy_conf = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(copy_conf)

        if not hasattr(copy_conf, 'configurations'):
            self.stderr.write(
                self._color_text('The configuration file does not contain the \'configurations\' variable', 'red')
            )
            sys.exit(1)

        configurations = copy_conf.configurations
        if conf_name not in configurations:
            self.stderr.write(self._color_text(f'Configuration \'{conf_name}\' not found', 'red'))
            sys.exit(1)

        # Extract the selected configuration
        config = configurations[conf_name]

        # Prepare collected sources
        self.collected_sources = []

        # Determine start directory (defaulting to settings.BASE_DIR)
        start_dir = config.get('__start_dir__', settings.BASE_DIR)

        # Extract base options
        base_options = {
            'exclude': config.get('__exclude__', []),
            'add_paths': config.get('__add_paths__', False),
            'start_dir': start_dir
        }

        # Process the configuration
        self.process_config('', config, base_options)

        # Join the collected sources with two newlines
        final_text = '\n\n'.join(self.collected_sources)

        # Write to file or copy to clipboard
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(final_text)
                self.stdout.write(self._color_text(f'Result saved to file: {output_file}', 'green'))
            except Exception as e:
                self.stderr.write(self._color_text(f'Error writing to file {output_file}: {str(e)}', 'red'))
        else:
            try:
                import pyperclip
            except ImportError:
                pyperclip = None
            if pyperclip:
                pyperclip.copy(final_text)
                self.stdout.write(self._color_text('Result copied to clipboard', 'green'))
            else:
                self.stderr.write(
                    self._color_text('pyperclip module is not installed. Could not copy to clipboard.', 'red')
                )

    def process_config(self, prefix, conf_item, opts):
        '''
        Recursively processes the configuration dictionary.
        - If conf_item is a dict (and not a special directive), we descend into that directory or that sub-structure.
        - If conf_item == '__copy__', we copy the corresponding file or directory (possibly with extension fallback).
        '''
        if isinstance(conf_item, dict):
            # Merge local exclude, add_paths, and start_dir if redefined
            local_options = opts.copy()
            for special in ['__exclude__', '__add_paths__', '__start_dir__']:
                if special in conf_item:
                    if special == '__exclude__':
                        local_options['exclude'] = conf_item[special]
                    elif special == '__add_paths__':
                        local_options['add_paths'] = conf_item[special]
                    elif special == '__start_dir__':
                        local_options['start_dir'] = conf_item[special]

            # For each key-value pair that doesn't start with '__', recurse deeper
            for key, value in conf_item.items():
                if key.startswith('__'):
                    continue
                new_prefix = f'{prefix}.{key}' if prefix else key
                self.process_config(new_prefix, value, local_options)

        elif isinstance(conf_item, str):
            if conf_item == '__copy__':
                # We want to copy the file or directory at 'prefix'
                try:
                    path_to_copy = self.resolve_path(prefix, opts['start_dir'])
                    self.copy_path(path_to_copy, opts)
                    self.stdout.write(self._color_text(f'Copied: {prefix}', 'green'))
                except FileNotFoundError as er:
                    self.stderr.write(self._color_text(f'Not found: {prefix} ({str(er)})', 'red'))
                except Exception as er:
                    self.stderr.write(self._color_text(f'Error copying {prefix}: {str(er)}', 'red'))
            else:
                self.stderr.write(self._color_text(f'Unknown directive \'{conf_item}\' for {prefix}', 'red'))
        else:
            self.stderr.write(self._color_text(f'Invalid configuration for {prefix}', 'red'))

    def resolve_path(self, dotted_path, start_dir):
        '''
        Converts a dotted path (e.g., "apps.core.routes.root") into a filesystem path
        relative to the given start_dir. If the exact path doesn't exist,
        tries appending known extensions (e.g., .py, .js, .jsx, etc.).
        Raises FileNotFoundError if the path does not exist after all attempts.
        '''
        parts = dotted_path.split('.')
        base_path = os.path.join(start_dir, *parts)

        # 1) If it exists as-is (folder or file), return immediately
        if os.path.exists(base_path):
            return base_path

        # 2) Otherwise, try appending known extensions
        for ext in self.KNOWN_EXTENSIONS:
            test_path = base_path + ext
            if os.path.exists(test_path):
                return test_path

        # If we still haven't found a match, raise an error
        raise FileNotFoundError(f'Path does not exist: {base_path}')

    def copy_path(self, path_to_copy, opts):
        '''
        Copies the content of a file or an entire directory into the collected_sources list.
        If path_to_copy is a directory, it is traversed recursively, respecting exclude rules.
        If path_to_copy is a file, it is read and possibly prepended with a path comment.
        '''
        if os.path.isdir(path_to_copy):
            self.copy_directory(path_to_copy, opts)
        else:
            self.copy_file(path_to_copy, opts)

    def copy_directory(self, directory_path, opts):
        '''
        Recursively copies all files from the given directory, skipping folders/files
        that match any of the substrings in opts['exclude'].
        '''
        for root, dirs, files in os.walk(directory_path):
            # Exclude directories
            dirs[:] = [
                d for d in dirs
                if not any(excl in d for excl in opts.get('exclude', []))
            ]
            for file in files:
                if any(excl in file for excl in opts.get('exclude', [])):
                    continue
                file_full = os.path.join(root, file)
                # Copy file
                self.copy_file(file_full, opts)

    def copy_file(self, file_path, opts):
        '''
        Reads the file, optionally prepends a path comment, and appends the result to collected_sources.
        '''
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        if opts.get('add_paths'):
            content = self.add_path_comment(content, file_path, opts['start_dir'])
        self.collected_sources.append(content)

    @staticmethod
    def add_path_comment(source, file_path, start_dir):
        '''
        Adds a comment with the relative path from start_dir to the beginning of the source code.
        If the source code already begins with a comment (containing at least one '/'),
        that line is removed before inserting the new comment.
        The comment style is chosen based on the file extension, using forward slashes.
        '''
        rel_path = os.path.relpath(file_path, start_dir).replace('\\', '/')

        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.py':
            new_comment = f'# {rel_path}\n'
        elif ext == '.js':
            new_comment = f'// {rel_path}\n'
        elif ext == '.jsx' or ext == '.tsx' or ext == '.ts':
            new_comment = f'// {rel_path}\n'
        elif ext == '.html':
            new_comment = f'<!-- {rel_path} -->\n'
        elif ext == '.css':
            new_comment = f'/* {rel_path} */\n'
        else:
            # Default comment style
            new_comment = f'# {rel_path}\n'

        lines = source.splitlines()
        if lines:
            first_line = lines[0].strip()
            # If the first line is a comment containing '/'
            if first_line.startswith(('#', '//', '/*', '<!--', '/')) and '/' in first_line:
                lines = lines[1:]
                source = '\n'.join(lines)

        return new_comment + source

    @staticmethod
    def _color_text(text, color):
        colors = {
            'red': '\033[31m',
            'green': '\033[32m',
            'reset': '\033[0m'
        }
        return f'{colors.get(color, "")}{text}{colors["reset"]}'
