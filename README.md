# 🚀 ADjango 

> Sometimes I use this in different projects, so I decided to put it on pypi

`ADjango` — это удобная библиотека для упрощения работы с Django, которая предлагает различные полезные менеджеры, сервисы, декораторы, утилиты для асинхронного программирования, планировщик задач для Celery, работу с транзакциями и многое другое.

- [Installation](#installation-)
- [Settings](#settings-)
- [Overview](#overview)
  - [Manager & Services](#manager--services-%EF%B8%8F)
  - [Utils](#utils-)
  - [Decorators](#decorators-)
  - [Other](#other)

## Installation 🛠️
```bash
pip install adjango
```

## Settings ⚙️

* ### Add the application to the project.
    ```python
    INSTALLED_APPS = [
        #...
        'adjango',
    ]
    ```
* ### In `settings.py` set the params
    ```python
    # settings.py
    # Ни один из параметров не является обязательным.  
  
    # For usage @a/controller decorators
    LOGIN_URL = '/login/' 
  
    # optional
    ADJANGO_BACKENDS_APPS = BASE_DIR / 'apps' # for management commands
    ADJANGO_FRONTEND_APPS = BASE_DIR.parent / 'frontend' / 'src' / 'apps' # for management commands
    ADJANGO_APPS_PREPATH = 'apps.'  # if apps in BASE_DIR/apps/app1,app2...
    ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION = ... # Read about @acontroller, @controller
    ADJANGO_CONTROLLERS_LOGGER_NAME = 'global' # only for usage @a/controller decorators
    ADJANGO_CONTROLLERS_LOGGING = True # only for usage @a/controller decorators
    ADJANGO_EMAIL_LOGGER_NAME = 'email' # for send_emails_task logging
    ```
    ```python
    MIDDLEWARE = [
        ...
        # add request.ip in views if u need
        'adjango.middleware.IPAddressMiddleware',  
        ...
    ]
    ```
## Overview
Most functions, if available in asynchronous form, are also available in synchronous form.

### Manager & Services 🛎️
Простой пример и сразу все понятно...
```python
from adjango.fields import AManyToManyField
from adjango.managers.base import AManager
from adjango.services.base import ABaseService
from adjango.managers.polymorphic import APolymorphicManager


class User(AbstractUser, ABaseService):
    objects = AManager()

class Product(Model, ABaseService):
    objects = AManager()
    # objects = APolymorphicManager() # ya u can
    name = CharField(max_length=100)

class Order(Model, ABaseService):
    objects = AManager()
    user = ForeignKey(User, CASCADE)
    products = AManyToManyField(Product)

# Теперь возможно следующее...
products = await Product.objects.aall()
products = await Product.objects.afilter(name='name')
# Возвращает объект либо None если не найдено
order = await Order.objects.agetorn(id=69) # aget or none
if not order: raise

# Устанавливаем продукты в заказ
await order.products.aset(products)
# Или queryset сразу...
await order.products.aset(
  Product.objects.filter(name='name') 
)
await order.products.aadd(products[0])

# Получаем снова заказ без связанных объектов
order: Order = await Order.objects.aget(id=69)
# Асинхронно получаем связанные объекты.
order.user = await order.arelated('user')
products = await order.products.aall()
# thk u
```
### Utils 🔧
  `aall`, `afilter`,  `arelated`, и так далее доступны как отдельные функции
  ```python
  from adjango.utils.funcs import aall, agetorn, afilter, aset, aadd, arelated
  ```
### Decorators 🎀
* `aforce_data`

    Декоратор `aforce_data` объединяет данные из `GET`, `POST` и `JSON` тела 
    запроса в `request.data`. Это упрощает доступ ко всем данным запроса в одном месте.

* `aatomic`

    Асинхронный декоратор, который оборачивает 
    функцию в транзакционный контекст. Если происходит исключение, все изменения откатываются.

* `acontroller / controller`

    Асинхронный декоратор, который оборачивает 
    функцию в транзакционный контекст. Если происходит исключение, все изменения откатываются.
    ```python
    from adjango.adecorators import acontroller

    @acontroller(name='MyView', logger='custom_logger', log_name=True, log_time=True)
    async def my_view(request):
        pass
  
    @acontroller('OneMoreView')
    async def my_view_one_more(request):
        pass
    ```
    * Эти декораторы автоматически отлавливают не отловленные исключения и логирует если логгер настроен 
    `ADJANGO_CONTROLLERS_LOGGER_NAME` `ADJANGO_CONTROLLERS_LOGGING`. 
    * Так же можно реализовать интерфейс:
        ```python
        class IHandlerControllerException(ABC):
            @staticmethod
            @abstractmethod
            def handle(fn_name: str, request: WSGIRequest | ASGIRequest, e: Exception, *args, **kwargs) -> None:
                """
                Пример функции обработки исключений.
        
                @param fn_name: Имя функции, в которой произошло исключение.
                @param request: Объект запроса (WSGIRequest или ASGIRequest).
                @param e: Исключение, которое нужно обработать.
                @param args: Позиционные аргументы, переданные в функцию.
                @param kwargs: Именованные аргументы, переданные в функцию.
        
                @return: None
                """
                pass
        ```
        и испрользовать `handle` для получении неотловленного исключения:
        ```python
        # settings.py
        from adjango.handlers import HCE # use my example if u need
        ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION = HCE.handle
        ```
    
### Other

* `AsyncAtomicContextManager`🧘

    Асинхронный контекст-менеджер для работы с транзакциями, который обеспечивает атомарность операций.
    ```python
    from adjango.utils.base import AsyncAtomicContextManager
    
    async def some_function():
        async with AsyncAtomicContextManager():
            ...  
    ```

* `Tasker`📋

    Класс Tasker предоставляет методы для планирования задач в `Celery` и `Celery Beat`.
    ```python
    from adjango.utils.tasks import Tasker
    
    task_id = Tasker.put(
        task=my_celery_task,
        param1='value1',
        param2='value2',
        countdown=60  # Задача выполнится через 60 секунд
    )
    ```
    ```python
    from adjango.utils.tasks import Tasker
    from datetime import datetime
    
    # Одноразовая задача через Celery Beat
    Tasker.beat(
        task=my_celery_task,
        name='one_time_task',
        schedule_time=datetime(2024, 10, 10, 14, 30),  # Запуск задачи 10 октября 2024 года в 14:30
        param1='value1',
        param2='value2'
    )
    
    # Периодическая задача через Celery Beat (каждый час)
    Tasker.beat(
        task=my_celery_task,
        name='hourly_task',
        interval=3600,  # Задача выполняется каждый час
        param1='value1',
        param2='value2'
    )
    ```

* `send_emails`

    Позволяет отправлять письма с использованием шаблонов и рендеринга контекста.
    ```python
    from adjango.utils.mail import send_emails
    
    send_emails(
        subject='Welcome!',
        emails=('user1@example.com', 'user2@example.com'),
        template='emails/welcome.html',
        context={'user': 'John Doe'}
    )
    ```
    ```python
    from adjango.tasks import send_emails_task
    from adjango.utils.tasks import Tasker
  
    send_emails_task.delay(
        subject='Hello!',
        emails=('user@example.com',),
        template='emails/hello.html',
        context={'message': 'Welcome to our service!'}
    )
    # or
    Tasker.put(
        task=send_emails_task,
        subject='Hello!',
        emails=('user@example.com',),
        template='emails/hello.html',
        context={'message': 'Welcome to our service!'},
        countdown=60  # Задача выполнится через 5 секунд
    )
    ```



