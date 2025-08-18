# querysets/polymorphic.py
try:
    from polymorphic.query import PolymorphicQuerySet
    from adjango.querysets.base import AQuerySet
    from adjango.utils.funcs import aall, agetorn, getorn, afilter, aset, aadd

    class APolymorphicQuerySet(AQuerySet, PolymorphicQuerySet):
        async def aall(self):
            return await aall(self)

        def getorn(self, exception=None, *args, **kwargs):
            return getorn(self, exception, *args, **kwargs)

        async def agetorn(self, exception=None, *args, **kwargs):
            return await agetorn(self, exception, *args, **kwargs)

        async def afilter(self, *args, **kwargs):
            return await afilter(self, *args, **kwargs)

        async def aset(self, data, *args, **kwargs):
            return await aset(self, data, *args, **kwargs)

        async def aadd(self, data, *args, **kwargs):
            return await aadd(self, data, *args, **kwargs)

except ImportError:
    pass
