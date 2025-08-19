# exceptions/base.py
from __future__ import annotations

import re
from enum import Enum
from typing import Any, Optional, Type

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

    class APIException(Exception):
        status_code = 500
        default_detail = _("Server Error")
        default_code = "error"

        def __init__(self, detail=None, code=None):
            super().__init__(detail or self.default_detail)
            self.detail = detail or self.default_detail
            self.default_code = code or self.default_code
            self.status_code = getattr(self, "status_code", 500)

    HTTP_400_BAD_REQUEST = 400
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_406_NOT_ACCEPTABLE = 406
    HTTP_408_REQUEST_TIMEOUT = 408
    HTTP_409_CONFLICT = 409
    HTTP_500_INTERNAL_SERVER_ERROR = 500
    HTTP_503_SERVICE_UNAVAILABLE = 503


__all__ = [
    "ApiExceptionGenerator",
    "ModelApiExcpetionGenerator",
    "ModelApiExcpetionBaseVariants",
]


def _slug_code(value: str) -> str:
    s = value.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "error"


def _model_verbose_name(model: Type[Any]) -> str:
    try:
        vn = getattr(getattr(model, "_meta", None), "verbose_name", None)
        if vn:
            return str(vn)
    except Exception:
        pass
    return model.__name__


class ApiExceptionGenerator(APIException):
    """
    Usage:
        raise ApiExceptionGenerator('Special error', 500)
        raise ApiExceptionGenerator('Special error', 500, 'special_error')
        raise ApiExceptionGenerator('Bad input', HTTP_400_BAD_REQUEST, extra={'field': 'email'})
    """

    def __init__(
        self,
        message: str,
        status: int,
        code: Optional[str] = None,
        extra: Optional[dict[str, Any]] = None,
    ) -> None:
        self.status_code = int(status)
        code_str = code or _slug_code(message)
        payload: dict[str, Any] = {"message": message}
        if extra:
            payload.update(extra)
        # For DRF, pass `code` to have ErrorDetail carry it; also set default_code for parity.
        self.default_code = code_str  # type: ignore[attr-defined]
        super().__init__(detail=payload, code=code_str)


class ModelApiExcpetionBaseVariants(Enum):
    DoesNotExist = "does_not_exist"
    AlreadyExists = "already_exists"
    InvalidData = "invalid_data"
    AccessDenied = "access_denied"
    NotAcceptable = "not_acceptable"
    Expired = "expired"
    InternalServerError = "internal_server_error"
    AlreadyUsed = "already_used"
    NotUsed = "not_used"
    NotAvailable = "not_available"
    TemporarilyUnavailable = "temporarily_unavailable"
    ConflictDetected = "conflict_detected"
    LimitExceeded = "limit_exceeded"
    DependencyMissing = "dependency_missing"
    Deprecated = "deprecated"


_VARIANT_TO_STATUS: dict[ModelApiExcpetionBaseVariants, int] = {
    ModelApiExcpetionBaseVariants.DoesNotExist: HTTP_404_NOT_FOUND,
    ModelApiExcpetionBaseVariants.AlreadyExists: HTTP_409_CONFLICT,
    ModelApiExcpetionBaseVariants.InvalidData: HTTP_400_BAD_REQUEST,
    ModelApiExcpetionBaseVariants.AccessDenied: HTTP_403_FORBIDDEN,
    ModelApiExcpetionBaseVariants.NotAcceptable: HTTP_406_NOT_ACCEPTABLE,
    ModelApiExcpetionBaseVariants.Expired: HTTP_408_REQUEST_TIMEOUT,
    ModelApiExcpetionBaseVariants.InternalServerError: HTTP_500_INTERNAL_SERVER_ERROR,
    ModelApiExcpetionBaseVariants.AlreadyUsed: HTTP_409_CONFLICT,
    ModelApiExcpetionBaseVariants.NotUsed: HTTP_400_BAD_REQUEST,
    ModelApiExcpetionBaseVariants.NotAvailable: HTTP_503_SERVICE_UNAVAILABLE,
    ModelApiExcpetionBaseVariants.TemporarilyUnavailable: HTTP_503_SERVICE_UNAVAILABLE,
    ModelApiExcpetionBaseVariants.ConflictDetected: HTTP_409_CONFLICT,
    ModelApiExcpetionBaseVariants.LimitExceeded: HTTP_400_BAD_REQUEST,
    ModelApiExcpetionBaseVariants.DependencyMissing: HTTP_400_BAD_REQUEST,
    ModelApiExcpetionBaseVariants.Deprecated: HTTP_400_BAD_REQUEST,
}


def _variant_message(model_name: str, variant: ModelApiExcpetionBaseVariants) -> str:
    if variant is ModelApiExcpetionBaseVariants.DoesNotExist:
        return f"{model_name} " + _("does not exist")
    if variant is ModelApiExcpetionBaseVariants.AlreadyExists:
        return f"{model_name} " + _("already exists")
    if variant is ModelApiExcpetionBaseVariants.InvalidData:
        return _("Invalid data for") + f" {model_name}"
    if variant is ModelApiExcpetionBaseVariants.AccessDenied:
        return _("Access denied for") + f" {model_name}"
    if variant is ModelApiExcpetionBaseVariants.NotAcceptable:
        return _("Not acceptable for") + f" {model_name}"
    if variant is ModelApiExcpetionBaseVariants.Expired:
        return f"{model_name} " + _("expired")
    if variant is ModelApiExcpetionBaseVariants.InternalServerError:
        return _("Internal server error in") + f" {model_name}"
    if variant is ModelApiExcpetionBaseVariants.AlreadyUsed:
        return f"{model_name} " + _("already used")
    if variant is ModelApiExcpetionBaseVariants.NotUsed:
        return f"{model_name} " + _("not used")
    if variant is ModelApiExcpetionBaseVariants.NotAvailable:
        return f"{model_name} " + _("not available")
    if variant is ModelApiExcpetionBaseVariants.TemporarilyUnavailable:
        return f"{model_name} " + _("temporarily unavailable")
    if variant is ModelApiExcpetionBaseVariants.ConflictDetected:
        return f"{model_name} " + _("conflict detected")
    if variant is ModelApiExcpetionBaseVariants.LimitExceeded:
        return f"{model_name} " + _("limit exceeded")
    if variant is ModelApiExcpetionBaseVariants.DependencyMissing:
        return f"{model_name} " + _("dependency missing")
    if variant is ModelApiExcpetionBaseVariants.Deprecated:
        return f"{model_name} " + _("deprecated")
    return _("Error")


class ModelApiExcpetionGenerator(APIException):
    """
    Usage:
        raise ModelApiExcpetionGenerator(model=Order, variant=ModelApiExcpetionBaseVariants.AlreadyExists)
        raise ModelApiExcpetionGenerator(Order, ModelApiExcpetionBaseVariants.DoesNotExist, code="order_not_found", extra={"id": 123})
    """

    def __init__(
        self,
        model: Type[Any],
        variant: ModelApiExcpetionBaseVariants,
        code: Optional[str] = None,
        extra: Optional[dict[str, Any]] = None,
    ) -> None:
        model_name = _model_verbose_name(model)
        message = _variant_message(model_name, variant)
        status = _VARIANT_TO_STATUS.get(variant, HTTP_500_INTERNAL_SERVER_ERROR)
        self.status_code = int(status)
        code_str = code or _slug_code(str(variant.value))
        payload: dict[str, Any] = {"message": message}
        if extra:
            payload.update(extra)
        self.default_code = code_str
        super().__init__(detail=payload, code=code_str)
