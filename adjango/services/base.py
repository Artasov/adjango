from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from adjango.models import AModel


class ABaseService(ABC):
    @abstractmethod
    def __init__(self, obj: 'AModel') -> None:
        self.obj: 'AModel' = obj
