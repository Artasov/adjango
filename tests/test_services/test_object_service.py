import pytest

from adjango.models.base import AModel
from adjango.services.base import ABaseService


class DummyService(ABaseService):
    def __init__(self, obj):
        super().__init__(obj)


class DummyModel(AModel):
    class Meta:
        app_label = "test_services"

    @property
    def service(self) -> DummyService:
        return DummyService(self)


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
    class NoServiceModel(AModel):
        class Meta:
            app_label = "test_services"

    with pytest.raises(NotImplementedError):
        NoServiceModel().service
