from django.core.cache import cache as djc

MIN_1 = 1 * 60
MIN_5 = 5 * 60
MIN_10 = 10 * 60
MIN_15 = 15 * 60
MIN_20 = 20 * 60
MIN_25 = 25 * 60
MIN_30 = 30 * 60
MIN_40 = 40 * 60
MIN_50 = 50 * 60
HOUR_1 = 1 * 60 * 60
HOUR_2 = 2 * 60 * 60
HOUR_3 = 3 * 60 * 60
HOUR_4 = 4 * 60 * 60
HOUR_5 = 5 * 60 * 60
HOUR_6 = 6 * 60 * 60
HOUR_7 = 7 * 60 * 60
HOUR_8 = 8 * 60 * 60
HOUR_9 = 9 * 60 * 60
HOUR_10 = 10 * 60 * 60
HOUR_11 = 11 * 60 * 60
HOUR_12 = 12 * 60 * 60
HOUR_13 = 13 * 60 * 60
HOUR_14 = 14 * 60 * 60
HOUR_15 = 15 * 60 * 60
HOUR_16 = 16 * 60 * 60
HOUR_17 = 17 * 60 * 60
HOUR_18 = 18 * 60 * 60
HOUR_19 = 19 * 60 * 60
HOUR_20 = 20 * 60 * 60
HOUR_21 = 21 * 60 * 60
HOUR_22 = 22 * 60 * 60
HOUR_23 = 23 * 60 * 60
DAY_1 = 1 * 60 * 60 * 24
DAYS_2 = 2 * 60 * 60 * 24
DAYS_3 = 3 * 60 * 60 * 24
DAYS_4 = 4 * 60 * 60 * 24
DAYS_5 = 5 * 60 * 60 * 24
DAYS_6 = 6 * 60 * 60 * 24
DAYS_7 = 7 * 60 * 60 * 24
DAYS_8 = 8 * 60 * 60 * 24
DAYS_9 = 9 * 60 * 60 * 24
DAYS_10 = 10 * 60 * 60 * 24
DAYS_11 = 11 * 60 * 60 * 24
DAYS_12 = 12 * 60 * 60 * 24
DAYS_13 = 13 * 60 * 60 * 24
DAYS_14 = 14 * 60 * 60 * 24
DAYS_15 = 15 * 60 * 60 * 24
DAYS_16 = 16 * 60 * 60 * 24
DAYS_17 = 17 * 60 * 60 * 24
DAYS_18 = 18 * 60 * 60 * 24
DAYS_19 = 19 * 60 * 60 * 24
DAYS_20 = 20 * 60 * 60 * 24


class CacheNotFound(Exception): pass


class Rediser:
    """Рофлан класыч для удобного использования кэширования в Django."""

    @staticmethod
    def cache(name, obj=None, timeout=HOUR_12, *args, **kwargs):
        """
        Кэширует результат функции или возвращает кэшированный результат, если он доступен.

        @param name: Базовое имя кэш-записи.
        @param obj: Объект или функция для кэширования.
        @param timeout: Время в секундах до истечения срока действия.
        @return: Кэшированный результат или результат вызова функции.
        """
        if djc.get(name) is not None: return False, djc.get(name)
        if obj is None:
            raise CacheNotFound(f'No cache found for {name}')
        else:
            result = obj(*args, **kwargs) if callable(obj) else obj
            djc.set(name, result, timeout=timeout)
            return True, result

    @staticmethod
    async def acache(name, obj=None, timeout=HOUR_12, *args, **kwargs):
        """
        Асинхронно кэширует результат функции или возвращает кэшированный результат, если он доступен.

        @param name: Базовое имя кэш-записи.
        @param obj: Объект или функция для кэширования.
        @param timeout: Время в секундах до истечения срока действия.
        @return: Кэшированный результат или результат вызова функции.
        """
        if djc.get(name) is not None: return False, djc.get(name)
        if obj is None:
            raise CacheNotFound(f'No cache found for {name}')
        else:
            result = await obj(*args, **kwargs) if callable(obj) else obj
            djc.set(name, result, timeout=timeout)
            return True, result

    @staticmethod
    def delete(name):
        djc.delete(name)

    @staticmethod
    def delete_all():
        djc.clear()
