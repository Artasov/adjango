# models/choices.py
from typing import Any, Optional

from django.db.models import IntegerChoices, TextChoices

__all__ = ['AChoicesMixin', 'ATextChoices', 'AIntegerChoices']


class AChoicesMixin:
    @classmethod
    def get_label(cls, value: Any) -> Optional[str]:
        """
        Return human-readable label for value or enum member.
        If value is invalid, returns None.
        """
        if isinstance(value, cls):
            return value.label

        try:
            return cls(value).label
        except (ValueError, KeyError, TypeError):
            return None

    @classmethod
    def has_value(cls, value: Any) -> bool:
        """
        Check whether enum has the passed value or enum member.
        """
        if isinstance(value, cls):
            return True

        try:
            cls(value)
            return True
        except (ValueError, KeyError, TypeError):
            return False

    @classmethod
    def as_dict(cls) -> dict[Any, str]:
        """
        Return choices as value-to-label mapping.
        """
        return {member.value: member.label for member in cls}


class ATextChoices(AChoicesMixin, TextChoices):
    """
    Enhanced TextChoices with helper methods.
    """


class AIntegerChoices(AChoicesMixin, IntegerChoices):
    """
    Enhanced IntegerChoices with helper methods.
    """
