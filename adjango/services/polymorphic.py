# services/polymorphic.py
try:
    from asgiref.sync import sync_to_async
    from polymorphic.models import PolymorphicModel

    from adjango.services.base import ABaseService


    class APolymorphicBaseService(ABaseService):
        async def aget_real_instance(self: PolymorphicModel):
            """
            Асинхронно получает реальный экземпляр полиморфной модели.

            :return: Реальный экземпляр модели или None, если он не найден.
            """
            return await sync_to_async(self.get_real_instance)()
except ImportError:
    pass
