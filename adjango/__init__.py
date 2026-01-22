"""
Adjango - Enhanced Django utilities and patterns.

Provides:
- Enhanced models with service integration
- Async/sync decorators and utilities
- Celery integration helpers
- Testing utilities
- Exception handling patterns
"""

__author__ = 'xlartas'


# Lazy imports to avoid Django setup issues
def __getattr__(name):
    """Lazy import to avoid Django setup issues."""
    if name == 'Model':
        from adjango.models.base import Model

        return Model
    elif name == 'BaseService':
        from adjango.services.base import BaseService

        return BaseService
    elif name == 'controller':
        from adjango.decorators import controller

        return controller
    elif name == 'acontroller':
        from adjango.adecorators import acontroller

        return acontroller
    elif name == 'task':
        from adjango.decorators import task

        return task
    elif name == 'force_data':
        from adjango.decorators import force_data

        return force_data
    elif name == 'aforce_data':
        from adjango.adecorators import aforce_data

        return aforce_data
    elif name == 'aatomic':
        from adjango.adecorators import aatomic

        return aatomic
    elif name == 'Tasker':
        from adjango.utils.celery.tasker import Tasker

        return Tasker
    raise AttributeError(f'module \'adjango\' has no attribute \'{name}\'')


__all__ = [
    'Model',
    'BaseService',
    'controller',
    'acontroller',
    'task',
    'force_data',
    'aforce_data',
    'aatomic',
    'Tasker',
]
