# 🚀 ADjango 

> Sometimes I use this in different projects, so I decided to put it on pypi

`ADjango` is a convenient library for simplifying work with Django, which offers various useful managers, services, decorators, utilities for asynchronous programming, a task scheduler for Celery, working with transactions and much more.
- [Installation](#installation-%EF%B8%8F)
- [Settings](#settings-%EF%B8%8F)
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
    # None of the parameters are required.  
  
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
A simple example and everything is immediately clear...
```python
from adjango.fields import AManyToManyField
from adjango.managers.base import AManager
from adjango.services.base import ABaseService
from adjango.models import AModel
from adjango.polymorphic_models import APolymorphicModel

class User(AbstractUser, ABaseService):
    objects = AManager()
# Its equal with...
class User(AbstractUser, AModel): pass
    

class Product(APolymorphicModel):
    # APolymorphicManager() of course here already exists
    name = CharField(max_length=100)

class Order(AModel):
    user = ForeignKey(User, CASCADE)
    products = AManyToManyField(Product)

    
# The following is now possible...
products = await Product.objects.aall()
products = await Product.objects.afilter(name='name')
# Returns an object or None if not found
order = await Order.objects.agetorn(id=69) # aget or none
if not order: raise

# We install products in the order
await order.products.aset(products)
# Or queryset right away...
await order.products.aset(
  Product.objects.filter(name='name') 
)
await order.products.aadd(products[0])

# We get the order again without associated objects
order: Order = await Order.objects.aget(id=69)
# Retrieve related objects asynchronously.
order.user = await order.related('user')
products = await order.products.aall()
# Works the same with intermediate processing/query filters
orders = await Order.objects.prefetch_related('products').aall()
for o in orders:
    for p in o.products.all():
        print(p.id)
#thk u
```
### Utils 🔧
  `aall`, `afilter`,  `arelated`, и так далее доступны как отдельные функции
  ```python
  from adjango.utils.funcs import aall, agetorn, afilter, aset, aadd, arelated
  ```
### Decorators 🎀
* `aforce_data`

    The `aforce_data` decorator combines data from the `GET`, `POST` and `JSON` body 
    request in `request.data`. This makes it easy to access all request data in one place.

* `atomic`

    An asynchronous decorator that wraps 
    function into a transactional context. If an exception occurs, all changes are rolled back.

* `acontroller/controller`

    An asynchronous decorator that wraps 
    function into a transactional context. If an exception occurs, all changes are rolled back.
    ```python
    from adjango.adecorators import acontroller

    @acontroller(name='My View', logger='custom_logger', log_name=True, log_time=True)
    async def my_view(request):
        pass
  
    @acontroller('One More View')
    async def my_view_one_more(request):
        pass
    ```
    * These decorators automatically catch uncaught exceptions and log if the logger is configured 
    `ADJANGO_CONTROLLERS_LOGGER_NAME` `ADJANGO_CONTROLLERS_LOGGING`. 
    * You can also implement the interface:
        ```python
        class IHandlerControllerException(ABC):
            @staticmethod
            @abstractmethod
            def handle(fn_name: str, request: WSGIRequest | ASGIRequest, e: Exception, *args, **kwargs) -> None:
                """
                An example of an exception handling function.
        
                @param fn_name: The name of the function where the exception occurred.
                @param request: The request object (WSGIRequest or ASGIRequest).
                @param e: The exception to be handled.
                @param args: Positional arguments passed to the function.
                @param kwargs: Named arguments passed to the function.
        
                @return: None
                """
                pass
        ```
        and use `handle` to get an uncaught exception:
        ```python
        # settings.py
        from adjango.handlers import HCE # use my example if u need
        ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION = HCE.handle
        ```
    
### Other

* `AsyncAtomicContextManager`🧘

    An asynchronous context manager for working with transactions, which ensures the atomicity of operations.
    ```python
    from adjango.utils.base import AsyncAtomicContextManager
    
    async def some_function():
        async with AsyncAtomicContextManager():
            ...  
    ```

* `Tasker`📋

    The Tasker class provides methods for scheduling tasks in `Celery` and `Celery Beat`.
    ```python
    from adjango.utils.tasks import Tasker
    
    task_id = Tasker.put(
        task=my_celery_task,
        param1='value1',
        param2='value2',
        countdown=60 # The task will be completed in 60 seconds
    )
    ```
    ```python
    from adjango.utils.tasks import Tasker
    from datetime import datetime
    
    # One-time task via Celery Beat
    Tasker.beat(
        task=my_celery_task,
        name='one_time_task',
        schedule_time=datetime(2024, 10, 10, 14, 30), # Start the task on October 10, 2024 at 14:30
        param1='value1',
        param2='value2'
    )
    
    # Periodic task via Celery Beat (every hour)
    Tasker.beat(
        task=my_celery_task,
        name='hourly_task',
        interval=3600, # The task runs every hour
        param1='value1',
        param2='value2'
    )
    ```

* `send_emails`

    Allows you to send emails using templates and context rendering.
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
        countdown=60 # The task will be completed in 5 seconds
    )
    ```