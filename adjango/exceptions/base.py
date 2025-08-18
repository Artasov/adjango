# exceptions/base.py
from typing import Optional, Type

from django.utils.translation import gettext_lazy as _

try:
    from rest_framework.exceptions import APIException
    from rest_framework.status import (
        HTTP_400_BAD_REQUEST,
        HTTP_403_FORBIDDEN,
        HTTP_404_NOT_FOUND,
        HTTP_406_NOT_ACCEPTABLE,
        HTTP_408_REQUEST_TIMEOUT,
        HTTP_409_CONFLICT,
        HTTP_500_INTERNAL_SERVER_ERROR,
        HTTP_503_SERVICE_UNAVAILABLE,
    )
except ImportError:
    pass


class BaseApiEx:
    DoesNotExist: Type[APIException]
    AlreadyExists: Type[APIException]
    InvalidData: Type[APIException]
    AccessDenied: Type[APIException]
    BadRequest: Type[APIException]
    Unauthorized: Type[APIException]
    MethodNotAllowed: Type[APIException]
    NotAcceptable: Type[APIException]
    RequestTimeout: Type[APIException]
    InternalServerError: Type[APIException]
    # Additional exceptions will be merged here.


class ModelApiBaseException:
    """
    Mixin to provide models with a set of API exceptions.
    Usage: MyModel.ApiEx.DoesNotExist (where MyModel is a subclass).
    You can extend the set via a nested ApiEx class.
    """

    class _ApiExDescriptor:
        def __init__(self, custom_ex: Optional[Type] = None):
            self._custom_ex = custom_ex  # Store custom exceptions defined in the subclass

        def __get__(self, instance, owner) -> Type[BaseApiEx]:
            # 'owner' is the class (e.g., Client) through which the descriptor is accessed.
            actual_owner = owner

            class DoesNotExist(APIException):
                status_code = HTTP_404_NOT_FOUND
                default_detail = {"message": f"{actual_owner.__name__} " + _("does not exist")}
                default_code = f"{actual_owner.__name__.lower()}_does_not_exist"

            class AlreadyExists(APIException):
                status_code = HTTP_409_CONFLICT
                default_detail = {"message": f"{actual_owner.__name__} " + _("already exists")}
                default_code = f"{actual_owner.__name__.lower()}_already_exists"

            class InvalidData(APIException):
                status_code = HTTP_400_BAD_REQUEST
                default_detail = {"message": _("Invalid data for") + f" {actual_owner.__name__}"}
                default_code = f"{actual_owner.__name__.lower()}_invalid_data"

            class AccessDenied(APIException):
                status_code = HTTP_403_FORBIDDEN
                default_detail = {"message": _("Access denied for") + f" {actual_owner.__name__}"}
                default_code = f"{actual_owner.__name__.lower()}_access_denied"

            class NotAcceptable(APIException):
                status_code = HTTP_406_NOT_ACCEPTABLE
                default_detail = {"message": _("Not acceptable for") + f" {actual_owner.__name__}"}
                default_code = f"{actual_owner.__name__.lower()}_not_acceptable"

            class Expired(APIException):
                status_code = HTTP_408_REQUEST_TIMEOUT
                default_detail = {"message": f"{actual_owner.__name__}" + _(" expired")}
                default_code = f"{actual_owner.__name__.lower()}_expired"

            class InternalServerError(APIException):
                status_code = HTTP_500_INTERNAL_SERVER_ERROR
                default_detail = {"message": _("Internal server error in") + f" {actual_owner.__name__}"}
                default_code = f"{actual_owner.__name__.lower()}_internal_server_error"

            class AlreadyUsed(APIException):
                status_code = HTTP_409_CONFLICT
                default_detail = {"message": f"{actual_owner.__name__} " + _("already used")}
                default_code = f"{actual_owner.__name__.lower()}_already_used"

            class NotUsed(APIException):
                status_code = HTTP_400_BAD_REQUEST
                default_detail = {"message": f"{actual_owner.__name__} " + _("not used")}
                default_code = f"{actual_owner.__name__.lower()}_not_used"

            class NotAvailable(APIException):
                status_code = HTTP_503_SERVICE_UNAVAILABLE
                default_detail = {"message": f"{actual_owner.__name__} " + _("not available")}
                default_code = f"{actual_owner.__name__.lower()}_not_available"

            class TemporarilyUnavailable(APIException):
                status_code = HTTP_503_SERVICE_UNAVAILABLE
                default_detail = {"message": f"{actual_owner.__name__} " + _("temporarily unavailable")}
                default_code = f"{actual_owner.__name__.lower()}_temporarily_unavailable"

            class ConflictDetected(APIException):
                status_code = HTTP_409_CONFLICT
                default_detail = {"message": f"{actual_owner.__name__} " + _("conflict detected")}
                default_code = f"{actual_owner.__name__.lower()}_conflict_detected"

            class LimitExceeded(APIException):
                status_code = HTTP_400_BAD_REQUEST
                default_detail = {"message": f"{actual_owner.__name__} " + _("limit exceeded")}
                default_code = f"{actual_owner.__name__.lower()}_limit_exceeded"

            class Deprecated(APIException):
                status_code = HTTP_400_BAD_REQUEST
                default_detail = {"message": f"{actual_owner.__name__} " + _(" deprecated")}
                default_code = f"{actual_owner.__name__.lower()}_deprecated"

            class DependencyMissing(APIException):
                status_code = HTTP_400_BAD_REQUEST
                default_detail = {"message": f"{actual_owner.__name__} " + _("dependency missing")}
                default_code = f"{actual_owner.__name__.lower()}_dependency_missing"

            additional_exceptions = {
                "AlreadyUsed": AlreadyUsed,
                "NotUsed": NotUsed,
                "NotAvailable": NotAvailable,
                "TemporarilyUnavailable": TemporarilyUnavailable,
                "ConflictDetected": ConflictDetected,
                "LimitExceeded": LimitExceeded,
                "DependencyMissing": DependencyMissing,
                "Expired": Expired,
            }

            base_exceptions = {
                "DoesNotExist": DoesNotExist,
                "AlreadyExists": AlreadyExists,
                "InvalidData": InvalidData,
                "AccessDenied": AccessDenied,
                "NotAcceptable": NotAcceptable,
                "InternalServerError": InternalServerError,
            }

            merged_exceptions: dict[str, type] = {}
            merged_exceptions.update(base_exceptions)
            merged_exceptions.update(additional_exceptions)

            # If custom exceptions are defined in subclass, merge them
            custom_ex = getattr(owner, "_custom_api_ex", None)
            if custom_ex is not None:
                for key, value in vars(custom_ex).items():
                    if not key.startswith("__") and isinstance(value, type) and issubclass(value, APIException):
                        merged_exceptions[key] = value

            return type("ApiEx", (BaseApiEx,), merged_exceptions)

    ApiEx = _ApiExDescriptor()

    def __init_subclass__(cls, **kwargs):
        """
        When a subclass is created, check if it defines a custom nested ApiEx.
        If so, store it on a special attribute (_custom_api_ex) and replace ApiEx with our descriptor.
        """
        super().__init_subclass__(**kwargs)
        custom = cls.__dict__.get("ApiEx", None)
        # If a custom ApiEx is defined directly in the subclass body (not inherited),
        # store it in _custom_api_ex.
        if custom is not None and not isinstance(custom, ModelApiBaseException._ApiExDescriptor):
            cls._custom_api_ex = custom
        cls.ApiEx = ModelApiBaseException._ApiExDescriptor()
