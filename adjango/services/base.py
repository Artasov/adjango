from abc import ABC, abstractmethod

from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from adjango.models import AModel

ModelT = TypeVar('ModelT', bound='AModel[Any]')


class ABaseService(Generic[ModelT], ABC):
    @abstractmethod
    def __init__(self, obj: ModelT) -> None:
        self.obj: ModelT = obj
