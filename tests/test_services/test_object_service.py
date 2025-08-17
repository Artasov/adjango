import pytest

from adjango.services.base import ABaseService
from adjango.services.object.base import ABaseModelObjectService


class DummyService(ABaseService):
    def __init__(self, obj):
        super().__init__(obj)


class DummyModel(ABaseModelObjectService[DummyService]):
    service_class = DummyService


@pytest.mark.asyncio
async def test_arelated_method():
    obj = DummyModel()
    obj.attr = "value"
    assert await obj.arelated("attr") == "value"


def test_service_property():
    obj = DummyModel()
    service = obj.service
    assert isinstance(service, DummyService)
    assert service.obj is obj


def test_service_property_not_implemented():
    class NoServiceModel(ABaseModelObjectService):
        pass

    with pytest.raises(NotImplementedError):
        NoServiceModel().service
