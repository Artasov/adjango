# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ADjango is a comprehensive library that enhances Django development with asynchronous features, Django REST Framework (DRF), and Celery integration. It provides services, serializers, decorators, and utilities for streamlining Django DRF Celery development.

**Key Technologies:**
- Django 4.2+
- Django REST Framework
- Celery with django-celery-beat
- Daphne (ASGI server)
- pytest for testing

## Development Commands

### Testing
```bash
# Run all tests with coverage report
pytest

# Run specific test file
pytest tests/test_adecorators.py

# Run tests with verbose output
pytest -v

# Run async tests only
pytest -m asyncio

# Coverage reports are generated in reports/ directory
# - HTML: reports/coverage_html/
# - pytest report: reports/pytest_report.html
```

### Code Formatting
```bash
# Format code with black (line length: 120)
black adjango/

# Format specific file
black adjango/models/base.py
```

### Celery Commands (via management commands)
```bash
# Start Celery worker
python manage.py celeryworker
python manage.py celeryworker --pool=solo --loglevel=info -E

# Start Celery beat scheduler
python manage.py celerybeat

# Purge Celery queues
python manage.py celerypurge
python manage.py celerypurge --queue=high
```

### Project Scaffolding
```bash
# Create new Django app with adjango structure
python manage.py astartup <app_name>

# Generate entities (models, services, serializers, tests) for app
python manage.py newentities <entity_name> <app_path> <Model1,Model2,...>
python manage.py newentities order apps.commerce Order,Product
```

## Architecture Overview

### Core Components

**1. ORM Async Usage**
- ADjango does not override Django managers or querysets
- Use Django's native async ORM methods (`aget`, `acreate`, `afirst`, etc.)

**2. Service Layer** (`adjango/services/`)
- `BaseService`: Base class for service layer pattern
- Services are accessed via model's `.service` property
- Encapsulates business logic separate from models
- Includes `getorn()` / `agetorn()` helpers for QuerySets
- Example: `user.service.get_full_name()`

**3. Models** (`adjango/models/`)
- `Model`: Base model with `arelated()` method for loading relations
- `PolymorphicModel`: Polymorphic model support (requires django-polymorphic)
- Mixins for common fields: `CreatedAtMixin`, `UpdatedAtMixin`, `CreatedUpdatedAtIndexedMixin`

**4. Async Serializers** (`adjango/aserializers.py`)
- `AModelSerializer`, `ASerializer`, `AListSerializer`: Async DRF serializers
- Support async methods: `adata`, `avalid_data`, `ais_valid`, `asave`
- Use with async views for non-blocking serialization

**5. Decorators** (`adjango/decorators.py`, `adjango/adecorators.py`)
- `@acontroller` / `@controller`: Automatic logging and exception handling for async/sync views
- `@aatomic`: Async transaction wrapper
- `@aforce_data`: Combines GET/POST/JSON data into `request.data`
- `@task`: Celery task logging decorator
- Configure via settings: `ADJANGO_CONTROLLERS_LOGGER_NAME`, `ADJANGO_CONTROLLERS_LOGGING`

**6. Exception Handling** (`adjango/exceptions/`)
- `ApiExceptionGenerator`: Generate API exceptions with HTTP status codes
- `ModelApiExceptionGenerator`: Model-specific exceptions with variants (DoesNotExist, AlreadyExists, InvalidData, etc.)
- Use `ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION` for custom exception handling

**7. Celery Integration** (`adjango/utils/celery/`, `adjango/tasks.py`)
- `Tasker`: Task scheduling utility with methods like `put()`, `beat()`, `abeat()`, `cancel_task()`
- Pre-built `send_emails_task` for async email sending
- Management commands: `celeryworker`, `celerybeat`, `celerypurge`

**8. Utilities** (`adjango/utils/`)
- `funcs.py`: Standalone async functions (`aall`, `afilter`, `arelated`, `aset`, `aadd`)
- `base.py`: `AsyncAtomicContextManager` for async transactions
- `common.py`: Utility functions like `get_full_name()`, `is_celery()`
- `mail.py`: Email sending utilities
- `crontab.py`: Crontab utilities

**9. Middleware** (`adjango/middleware.py`)
- `IPAddressMiddleware`: Adds `request.ip` to views (configure via `ADJANGO_IP_META_NAME`)

**10. Management Commands** (`adjango/management/commands/`)
- `astartproject`: Clone adjango-template
- `astartup`: Create app with service layer structure
- `newentities`: Generate models, services, serializers, tests
- `copy_project`: Copy project with configuration
- `dumpdata_to_dir` / `loaddata_from_dir`: Fixture management
- Celery commands: `celeryworker`, `celerybeat`, `celerypurge`

### Configuration

Key settings in `settings.py`:
```python
INSTALLED_APPS = [
    'adjango',  # Required
    # ...
]

MIDDLEWARE = [
    'adjango.middleware.IPAddressMiddleware',  # Optional: adds request.ip
    # ...
]

# Optional adjango settings
LOGIN_URL = '/login/'  # For @controller auth_required
ADJANGO_BACKENDS_APPS = BASE_DIR / 'apps'
ADJANGO_FRONTEND_APPS = BASE_DIR.parent / 'frontend' / 'src' / 'apps'
ADJANGO_APPS_PREPATH = 'apps.'  # if apps in BASE_DIR/apps/
ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION = handler_function
ADJANGO_CONTROLLERS_LOGGER_NAME = 'global'
ADJANGO_CONTROLLERS_LOGGING = True
ADJANGO_EMAIL_LOGGER_NAME = 'email'
ADJANGO_IP_LOGGER = 'global'
ADJANGO_IP_META_NAME = 'HTTP_X_FORWARDED_FOR'
```

### Test Structure

Tests are in `tests/` directory with test project in `tests/project/`:
- Test project settings: `tests/project/project/settings.py`
- Test app: `tests/project/app/`
- Use pytest with Django settings: `DJANGO_SETTINGS_MODULE=project.settings`
- Async tests marked with `@pytest.mark.asyncio`
- Coverage configured in `pytest.ini`

### Package Structure

```
adjango/
├── adecorators.py       # Async decorators
├── aserializers.py      # Async serializers
├── decorators.py        # Sync decorators
├── serializers.py       # Sync serializer utilities (dynamic_serializer)
├── middleware.py        # Middleware classes
├── handlers.py          # Exception handlers
├── tasks.py             # Celery tasks
├── models/              # Model base classes and mixins
├── services/            # Service layer base
├── exceptions/          # Exception generators
├── utils/               # Utilities
│   ├── celery/         # Celery utilities (Tasker)
│   ├── funcs.py        # Async helper functions
│   ├── base.py         # Base utilities (AsyncAtomicContextManager)
│   ├── common.py       # Common utilities
│   └── mail.py         # Email utilities
├── management/
│   └── commands/       # Django management commands
└── mixins/             # Model mixins
```

## Important Patterns

### Async/Sync Duality
- Most async functions have sync equivalents
- Async functions prefixed with `a`: `aget()` vs `get()`
- Use async functions in async views, sync in sync views

### Service Layer Pattern
```python
# Define service
class UserService(BaseService):
    def __init__(self, obj: 'User') -> None:
        super().__init__(obj)
        self.user = obj

# Add property to model
class User(AbstractUser):
    @property
    def service(self) -> UserService:
        return UserService(self)

# Use in views
user = await User.objects.aget(id=1)
result = user.service.some_method()
```

### Dynamic Serializers
Use `dynamic_serializer()` to create subset serializers from complete ones:
```python
from adjango.serializers import dynamic_serializer

TierOneSerializer = dynamic_serializer(
    CompleteSerializer,
    ('id', 'name')
)
```

### Exception Handling
```python
from adjango.exceptions.base import (
    ApiExceptionGenerator,
    ModelApiExceptionGenerator,
    ModelApiExceptionBaseVariant as MAEBV
)

# General exceptions
raise ApiExceptionGenerator('Error message', 400, 'error_code')

# Model exceptions
raise ModelApiExceptionGenerator(Order, MAEBV.DoesNotExist)
```

## When Making Changes

1. **Adding async methods**: Follow `a<method_name>` naming convention
2. **New utilities**: Place in appropriate `utils/` subdirectory
3. **New management commands**: Add to `management/commands/` with proper documentation
4. **Testing**: Write tests in `tests/` matching the module structure
5. **Type hints**: Use TYPE_CHECKING imports to avoid circular dependencies
6. **Service layer**: Keep business logic in services, not models or views
7. **Black formatting**: Code must follow black style (line-length=120)
