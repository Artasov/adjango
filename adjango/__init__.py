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
    if name == 'AModel':
        from adjango.models.base import AModel

        return AModel
    elif name == 'AAbstractUser':
        from adjango.models.base import AAbstractUser

        return AAbstractUser
    elif name == 'AManager':
        from adjango.managers.base import AManager

        return AManager
    elif name == 'AUserManager':
        from adjango.managers.base import AUserManager

        return AUserManager
    elif name == 'ABaseService':
        from adjango.services.base import ABaseService

        return ABaseService
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
    'AModel',
    'AAbstractUser',
    'AManager',
    'AUserManager',
    'ABaseService',
    'controller',
    'acontroller',
    'task',
    'force_data',
    'aforce_data',
    'aatomic',
    'Tasker',
]
