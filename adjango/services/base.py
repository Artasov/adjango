from abc import ABC

from adjango.models import AModel


class ABaseService(ABC):
    def __init__(self, obj: type(AModel)):
        self.obj = obj
