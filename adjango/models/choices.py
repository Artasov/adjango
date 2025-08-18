# models/choices.py
from typing import Optional

from django.db.models import TextChoices


class ATextChoices(TextChoices):
    @classmethod
    def get_label(cls, value) -> Optional[str]:
        """
        Returns human-readable label for passed value or Enum member.
        If value is invalid - returns None.
        """
        # If Enum member itself is passed - return its label directly
        if isinstance(value, cls):
            return value.label

        try:
            # Try to get member by its value and return its label
            return cls(value).label
        except (ValueError, KeyError, TypeError):
            return None
