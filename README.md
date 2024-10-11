# ADjango 

> Sometimes I use this in different projects, so I decided to put it on pypi

`ADjango` — это удобная библиотека для упрощения работы с Django, которая предлагает различные полезные декораторы, утилиты для асинхронного программирования, планировщик задач для Celery, работу с транзакциями и многое другое.

## Installation
```bash
pip install adjango
```

## Settings

* ### Add the application to the project.
    ```python
    INSTALLED_APPS = [
        #...
        'adjango',
    ]
    ```
* ### In `settings.py` set the params
    ```python
    # adjango
    from adjango.decorators import _handling_function
    
    LOGIN_URL = '/login/'
    ADJANGO_BACKENDS_APPS = BASE_DIR / 'apps'
    ADJANGO_FRONTEND_APPS = BASE_DIR.parent / 'frontend' / 'src' / 'apps'
    ADJANGO_APPS_PREPATH = 'apps.'  # if apps in BASE_DIR/apps/app1,app2...
    # ADJANGO_APPS_PREPATH = None # if in BASE_DIR/app1,app2...
    # Override _handling_function so that unhandled exceptions are handled as you wish
    ADJANGO_UNCAUGHT_EXCEPTION_HANDLING_FUNCTION = _handling_function
    ADJANGO_CONTROLLERS_LOGGER_NAME = 'global'
    ADJANGO_CONTROLLERS_LOGGING = True
    ADJANGO_EMAIL_LOGGER_NAME = 'email'
    ```
    ```python
    MIDDLEWARE = [
        ...
        # add request.ip in views
        'adjango.middleware.IPAddressMiddleware',  
        ...
    ]
    ```
## Overview
Most functions, if available in asynchronous form, are also available in synchronous form.
* `aforce_data`

    Декоратор `aforce_data` объединяет данные из `GET`, `POST` и `JSON` тела 
    запроса в `request.data`. Это упрощает доступ ко всем данным запроса в одном месте.

* `aatomic`

    Асинхронный декоратор, который оборачивает 
    функцию в транзакционный контекст. Если происходит исключение, все изменения откатываются.

* `aatomic`

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
* `AsyncAtomicContextManager`

    Асинхронный контекст-менеджер для работы с транзакциями, который обеспечивает атомарность операций.
    ```python
    from adjango.utils.base import AsyncAtomicContextManager
    
    async def some_function():
        async with AsyncAtomicContextManager():
            ...  
    ```

* `Tasker`

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



