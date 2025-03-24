from typing import Optional

from django.db.models import TextChoices


class ATextChoices(TextChoices):
    @classmethod
    def get_label(cls, value) -> Optional[str]:
        """
        Возвращает human‑readable label для переданного значения или Enum‑члена.
        Если значение некорректно — возвращает None.
        """
        # Если передан сам Enum‑член — сразу возвращаем его label
        if isinstance(value, cls):
            return value.label

        try:
            # Попытка получить член по его значению и вернуть его label
            return cls(value).label
        except (ValueError, KeyError):
            return None
