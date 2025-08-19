# 🚀 ADjango

📊 **[Coverage Report](reports/coverage_html/index.html) (60%)**

> Sometimes I use this in different projects, so I decided to put it on pypi

`ADjango` is a comprehensive library that enhances Django development with Django REST Framework (DRF) and Celery integration. It provides essential tools including asynchronous `managers`, `services`, `serializers`, `decorators`, `exceptions` and more utilities for `async` programming, Celery task scheduling, `transaction` management, and much more to streamline your Django DRF Celery development workflow.

- [🚀 ADjango](#-adjango)
  - [Installation 🛠️](#installation-️)
  - [Settings ⚙️](#settings-️)
  - [Overview](#overview)
    - [Manager \& Services 🛎️](#manager--services-️)
    - [Utils 🔧](#utils-)
    - [Mixins 🎨](#mixins-)
    - [Decorators 🎀](#decorators-)
    - [Exceptions 🚨](#exceptions-)
    - [Serializers 🔧](#serializers-)
    - [Management](#management)
    - [Celery 🔥](#celery-)
      - [Management Commands](#management-commands)
      - [@task Decorator](#task-decorator)
      - [Tasker - Task Scheduler](#tasker---task-scheduler)
      - [Email Sending via Celery](#email-sending-via-celery)
    - [Other](#other)

## Installation 🛠️

```bash
pip install adjango
```

## Settings ⚙️

- ### Add the application to the project

    ```python
    INSTALLED_APPS = [
        # ...
        'adjango',
    ]
    ```

- ### In `settings.py` set the params

    ```python
    # settings.py
  
    # NONE OF THE PARAMETERS ARE REQUIRED  
  
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
from adjango.models.base import AAbstractUser
from adjango.models.polymorphic import APolymorphicModel

...
...  # Service layer usage
...

# services/user.py
if TYPE_CHECKING:
  from apps.core.models import User


class UserService(ABaseService):
  def __init__(self, user: 'User') -> None:
    self.user = user

  def get_full_name(self) -> str:
    return f"{self.user.first_name} {self.user.last_name}"


# models/user.py (User redefinition)
class User(AAbstractUser):
  ...

  @property
  def service(self) -> UserService:
    return UserService(self)


# and u can use with nice type hints:
user = await User.objects.aget(id=1)
full_name = user.service.get_full_name()

...
...  # Other best features
...


# models/commerce.py
class Product(APolymorphicModel):
  name = CharField(max_length=100)


class Order(AModel):
  user = ForeignKey(User, CASCADE)
  products = AManyToManyField(Product)


# The following is now possible...
products = await Product.objects.aall()
products = await Product.objects.afilter(name='name')
# Returns an object or None if not found
order = await Order.objects.agetorn(id=69)  # aget or none
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
order.user = await order.arelated('user')
products = await order.products.aall()
# Works the same with intermediate processing/query filters
orders = await Order.objects.prefetch_related('products').aall()
for o in orders:
  for p in o.products.all():
    print(p.id)
# thk u
```

### Utils 🔧

`aall`, `afilter`,  `arelated`, and so on are available as individual functions

  ```python
  from adjango.utils.funcs import (
    aall, getorn, agetorn, 
    afilter, aset, aadd, arelated
  )
  ```

### Mixins 🎨

```python
from adjango.models.mixins import (
    ACreatedAtMixin, ACreatedAtIndexedMixin, ACreatedAtEditableMixin,
    AUpdatedAtMixin, AUpdatedAtIndexedMixin,
    ACreatedUpdatedAtMixin, ACreatedUpdatedAtIndexedMixin
)

class EventProfile(ACreatedUpdatedAtIndexedMixin):
    event = ForeignKey('events.Event', CASCADE, 'members', verbose_name=_('Event'))
    
    @property
    def service(self) -> EventProfileService:
        return EventProfileService(self)
```

### Decorators 🎀

- `aforce_data`

  The `aforce_data` decorator combines data from the `GET`, `POST` and `JSON` body
  request in `request.data`. This makes it easy to access all request data in one place.

- `aatomic`

  An asynchronous decorator that wraps function into a transactional context using `AsyncAtomicContextManager`. If an exception occurs, all database changes are rolled back.

- `acontroller/controller`

  Decorators that provide automatic logging and exception handling for views. The `acontroller` is for async views, `controller` is for sync views. They do NOT wrap functions in transactions (use `@aatomic` for that).

    ```python
    from adjango.adecorators import acontroller
    from adjango.decorators import controller

    @acontroller(name='My View', logger='custom_logger', log_name=True, log_time=True)
    async def my_view(request):
        pass
  
    @acontroller('One More View')
    async def my_view_one_more(request):
        pass

    @controller(name='Sync View', auth_required=True, log_time=True)
    def my_sync_view(request):
        pass
    ```

  - These decorators automatically catch uncaught exceptions and log them if the logger is configured via `ADJANGO_CONTROLLERS_LOGGER_NAME` and `ADJANGO_CONTROLLERS_LOGGING`.
  - The `controller` decorator also supports authentication checking with `auth_required` parameter.
  - You can also implement the interface:

    ```python
    class IHandlerControllerException(ABC):
        @staticmethod
        @abstractmethod
        def handle(fn_name: str, request: WSGIRequest | ASGIRequest, e: Exception, *args, **kwargs) -> None:
            """
            An example of an exception handling function.
    
            :param fn_name: The name of the function where the exception occurred.
            :param request: The request object (WSGIRequest or ASGIRequest).
            :param e: The exception to be handled.
            :param args: Positional arguments passed to the function.
            :param kwargs: Named arguments passed to the function.
    
            :return: None
            """
            pass
    ```

    and use `handle` to get an uncaught exception:

    ```python
    # settings.py
    from adjango.handlers import HCE # use my example if u need
    ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION = HCE.handle
    ```

### Exceptions 🚨

`ADjango` provides convenient classes for generating API exceptions with proper HTTP statuses and structured error messages.

```python
from adjango.exceptions.base import (
    ApiExceptionGenerator, 
    ModelApiExcpetionGenerator, 
    ModelApiExcpetionBaseVariants
)

# General API exceptions
raise ApiExceptionGenerator('Специальная ошибка', 500)
raise ApiExceptionGenerator('Специальная ошибка', 500, 'special_error')
raise ApiExceptionGenerator(
    'Неверные данные', 
    400, 
    extra={'field': 'email'}
)

# Model exceptions
from apps.commerce.models import Order

raise ModelApiExcpetionGenerator(
    model=Order, 
    variant=ModelApiExcpetionBaseVariants.DoesNotExist
)
raise ModelApiExcpetionGenerator(
    Order, 
    ModelApiExcpetionBaseVariants.AlreadyExists, 
    code="order_exists", 
    extra={"id": 123}
)

# Available exception variants for models:
# DoesNotExist, AlreadyExists, InvalidData, AccessDenied,
# NotAcceptable, Expired, InternalServerError, AlreadyUsed,
# NotUsed, NotAvailable, TemporarilyUnavailable, 
# ConflictDetected, LimitExceeded, DependencyMissing, Deprecated
```

### Serializers 🔧

`ADjango` extends `Django REST Framework` serializers to support asynchronous
operations, making it easier to handle data in async views.
Support methods like `adata`, `avalid_data`, `ais_valid`, and `asave`.

```python
from adjango.querysets.base import AQuerySet
from adjango.aserializers import (
    AModelSerializer, ASerializer, AListSerializer
)
from adjango.serializers import dynamic_serializer

...


class ConsultationPublicSerializer(AModelSerializer):
    clients = UserPublicSerializer(many=True, read_only=True)
    psychologists = UserPsyPublicSerializer(many=True, read_only=True)
    config = ConsultationConfigSerializer(read_only=True)

    class Meta:
        model = Consultation
        fields = '__all__'


# From the complete serializer we cut off the pieces into smaller ones
ConsultationSerializerTier1 = dynamic_serializer(
    ConsultationPublicSerializer, ('id', 'date',)
)
ConsultationSerializerTier2 = dynamic_serializer(
    ConsultationPublicSerializer, (
        'id', 'date', 'psychologists', 'clients', 'config'
    ), {
        'psychologists': UserPublicSerializer(many=True),  # overridden
    }
)


# Use it, in compact format
@acontroller('Completed Consultations')
@api_view(('GET',))
@permission_classes((IsAuthenticated,))
async def consultations_completed(request):
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 10))
    return Response({
        'results': await ConsultationSerializerTier2(
            await request.user.completed_consultations[
                  (page - 1) * page_size:page * page_size
                  ].aall(),
            many=True,
            context={'request': request}
        ).adata
    }, status=200)


...


class UserService(ABaseService['User']):
    ...

    @property
    def completed_consultations(self) -> AQuerySet['Consultation']:
        """
        Returns an optimized AQuerySet of all completed consultations of the user
        (both psychologist and client).
        """
        from apps.psychology.models import Consultation
        now_ = now()
        return Consultation.objects.defer(
            'communication_type',
            'language',
            'reserved_by',
            'notifies',
            'cancel_initiator',
            'original_consultation',
            'consultations_feedbacks',
        ).select_related(
            'config',
            'conference',
        ).prefetch_related(
            'clients',
            'psychologists',
        ).filter(
            Q(
                Q(clients=self.user) | Q(psychologists=self.user),
                status=Consultation.Status.PAID,
                date__isnull=False,
                date__lt=now_,
                consultations_feedbacks__user=self.user,
            ) |
            Q(
                Q(clients=self) | Q(psychologists=self.user),
                status=Consultation.Status.CANCELLED,
                date__isnull=False,
            )
        ).distinct().order_by('-updated_at')

    ...
```

### Management

- `copy_project`
  Documentation in the _py_ module itself - **[copy_project](adjango/management/commands/copy_project.py)**

ADjango ships with extra management commands to speed up project scaffolding.

- `astartproject` — clones the [adjango-template](https://github.com/Artasov/adjango-template)
  into the given directory and strips its Git history.

  ```bash
  django-admin astartproject myproject
  ```

- `astartup` — creates an app skeleton inside `apps/` and registers it in
  `INSTALLED_APPS`.

  ```bash
  python manage.py astartup blog
  ```

  After running the command you will have the following structure:

  ```sh
  apps/
      blog/
          controllers/base.py
          models/base.py
          services/base.py
          serializers/base.py
          tests/base.py
  ```

- `newentities` — generates empty exception, model, service, serializer and
  test stubs for the specified models in the target app.

  ```bash
  python manage.py newentities order apps.commerce Order,Product,Price
  ```

  Or create a single model:

  ```bash
  python manage.py newentities order apps.commerce Order
  ```

### Celery 🔥

ADjango provides convenient tools for working with Celery: management commands, decorators, and task scheduler.

For Celery configuration in Django, refer to the [official Celery documentation](https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html).

#### Management Commands

- `celeryworker` — starts Celery Worker with default settings

  ```bash
  python manage.py celeryworker
  python manage.py celeryworker --pool=solo --loglevel=info -E
  python manage.py celeryworker --concurrency=4 --queues=high_priority,default
  ```

- `celerybeat` — starts Celery Beat scheduler for periodic tasks

  ```bash
  python manage.py celerybeat
  python manage.py celerybeat --loglevel=debug
  ```

- `celerypurge` — clears Celery queues from unfinished tasks

  ```bash
  python manage.py celerypurge               # clear all queues
  python manage.py celerypurge --queue=high  # clear specific queue
  ```

#### @task Decorator

The `@task` decorator automatically logs Celery task execution, including errors:

```python
from celery import shared_task
from adjango.decorators import task

@shared_task
@task(logger="global")
def my_background_task(param1: str, param2: int) -> bool:
    """
    Task with automatic execution logging.
    """
    # your code here
    return True
```

**What the decorator provides:**

- ✅ Automatic logging of task start and completion
- ✅ Logging of task parameters
- ✅ Detailed error logging with stack trace
- ✅ Flexible logger configuration for different tasks

#### Tasker - Task Scheduler

The `Tasker` class provides convenient methods for scheduling and managing Celery tasks:

```python
from adjango.utils.celery.tasker import Tasker

# Immediate execution
task_id = Tasker.put(task=my_task, param1='value')

# Delayed execution (in 60 seconds)
task_id = Tasker.put(task=my_task, countdown=60, param1='value')

# Execution at specific time
from datetime import datetime
task_id = Tasker.put(
    task=my_task, 
    eta=datetime(2024, 12, 31, 23, 59),
    param1='value'
)

# Cancel task by ID
Tasker.cancel_task(task_id)

# One-time task via Celery Beat (sync)
Tasker.beat(
    task=my_task,
    name='one_time_task',
    schedule_time=datetime(2024, 10, 10, 14, 30),
    param1='value'
)

# Periodic task via Celery Beat (sync)
Tasker.beat(
    task=my_task,
    name='hourly_cleanup',
    interval=3600,  # every hour in seconds
    param1='value'
)

# Crontab schedule via Celery Beat (sync)
Tasker.beat(
    task=my_task,
    name='daily_report',
    crontab={'hour': 7, 'minute': 30},  # every day at 7:30 AM
    param1='value'
)

# Async version of beat is also available
await Tasker.abeat(
    task=my_task,
    name='async_task',
    interval=1800,  # every 30 minutes
    param1='value'
)
```

#### Email Sending via Celery

ADjango includes a ready-to-use task for sending emails with templates:

```python
from adjango.tasks import send_emails_task
from adjango.utils.mail import send_emails

# Synchronous sending
send_emails(
    subject='Welcome!',
    emails=('user@example.com',),
    template='emails/welcome.html',
    context={'user': 'John Doe'}
)

# Asynchronous sending via Celery
send_emails_task.delay(
    subject='Hello!',
    emails=('user@example.com',),
    template='emails/hello.html',
    context={'message': 'Welcome to our service!'}
)

# Via Tasker with delayed execution
Tasker.put(
    task=send_emails_task,
    subject='Reminder',
    emails=('user@example.com',),
    template='emails/reminder.html',
    context={'deadline': '2024-12-31'},
    countdown=3600  # send in an hour
)
```

### Other

- `AsyncAtomicContextManager`🧘

  An asynchronous context manager for working with transactions, which ensures the atomicity of operations.

    ```python
    from adjango.utils.base import AsyncAtomicContextManager
    
    async def some_function():
        async with AsyncAtomicContextManager():
            ...  
    ```
