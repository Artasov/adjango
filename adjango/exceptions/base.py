from typing import Type

from django.utils.translation import gettext_lazy as _

try:
    from rest_framework.exceptions import APIException
    from rest_framework.status import (
        HTTP_404_NOT_FOUND,
        HTTP_400_BAD_REQUEST,
        HTTP_409_CONFLICT, HTTP_403_FORBIDDEN,
    )
except ImportError:
    pass


# A base type for API exceptions to allow IDE type hints.
class BaseApiEx:
    DoesNotExist: Type[APIException]
    AlreadyExists: Type[APIException]
    InvalidData: Type[APIException]
    AccessDenied: Type[APIException]
    # Custom exceptions (if any) will be merged into this type.


class ModelApiBaseException:
    """
    Mixin to provide models with a set of API exceptions.
    Usage: MyModel.ApiEx.DoesNotExist (where MyModel is a subclass).
    You can extend the set via a nested ApiEx class.
    """

    class _ApiExDescriptor:
        def __init__(self, custom_ex: Type = None):
            self._custom_ex = custom_ex  # Store custom exceptions defined in the subclass

        def __get__(self, instance, owner) -> Type[BaseApiEx]:
            # 'owner' is the class (e.g., Client) through which the descriptor is accessed.
            actual_owner = owner

            # Define base exceptions using the child class's name.
            class DoesNotExist(APIException):
                status_code = HTTP_404_NOT_FOUND
                default_detail = {'message': f'{actual_owner.__name__} ' + _('does not exist')}
                default_code = f'{actual_owner.__name__.lower()}_does_not_exist'

            class AlreadyExists(APIException):
                status_code = HTTP_409_CONFLICT
                default_detail = {'message': f'{actual_owner.__name__} ' + _('already exists')}
                default_code = f'{actual_owner.__name__.lower()}_already_exists'

            class InvalidData(APIException):
                status_code = HTTP_400_BAD_REQUEST
                default_detail = {'message': _('Invalid data for') + f' {actual_owner.__name__}'}
                default_code = f'{actual_owner.__name__.lower()}_invalid_data'

            class AccessDenied(APIException):
                status_code = HTTP_403_FORBIDDEN
                default_detail = {'message': _('Access denied for') + f' {actual_owner.__name__}'}
                default_code = f'{actual_owner.__name__.lower()}_access_denied'

            merged_exceptions = {
                'DoesNotExist': DoesNotExist,
                'AlreadyExists': AlreadyExists,
                'InvalidData': InvalidData,
                'AccessDenied': AccessDenied,
            }

            # Retrieve custom exceptions stored on the subclass (if any)
            custom_ex = getattr(owner, '_custom_api_ex', None)
            if custom_ex is not None:
                for key, value in vars(custom_ex).items():
                    if not key.startswith('__') and isinstance(value, type) and issubclass(value, APIException):
                        merged_exceptions[key] = value

            # Return a new type that subclasses BaseApiEx with merged exceptions.
            return type('ApiEx', (BaseApiEx,), merged_exceptions)

    # By default, ApiEx is our descriptor.
    ApiEx = _ApiExDescriptor()

    def __init_subclass__(cls, **kwargs):
        """
        When a subclass is created, check if it defines a custom nested ApiEx.
        If so, store it on a special attribute (_custom_api_ex) and replace ApiEx with our descriptor.
        """
        super().__init_subclass__(**kwargs)
        custom = cls.__dict__.get('ApiEx', None)
        # If a custom ApiEx is defined directly in the subclass body (not inherited),
        # store it in _custom_api_ex.
        if custom is not None and not isinstance(custom, ModelApiBaseException._ApiExDescriptor):
            cls._custom_api_ex = custom
        cls.ApiEx = ModelApiBaseException._ApiExDescriptor()
