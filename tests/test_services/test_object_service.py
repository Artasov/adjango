import pytest

from adjango.models.base import Model
from adjango.services.base import BaseService


class DummyService(BaseService):
    def __init__(self, obj: 'DummyModel'):
        super().__init__(obj)


class DummyModel(Model):
    class Meta:
        app_label = 'test_services'

    @property
    def service(self) -> DummyService:
        return DummyService(self)


@pytest.mark.asyncio
async def test_arelated_method():
    obj = DummyModel()
    obj.attr = 'value'
    assert await obj.arelated('attr') == 'value'


def test_service_property():
    obj = DummyModel()
    service = obj.service
    assert isinstance(service, DummyService)


def test_service_property_not_implemented():
    class NoServiceModel(Model):
        class Meta:
            app_label = 'test_services'

    with pytest.raises(NotImplementedError):
        getattr(NoServiceModel(), 'service')
