# ADjango 

**ADjango** 
> Sometimes I use this in different projects, so I decided to put it on pypi

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
    LOGIN_URL = '/login/'
    ADJANGO_BACKENDS_APPS = BASE_DIR / 'apps'
    ADJANGO_FRONTEND_APPS = BASE_DIR.parent / 'frontend' / 'src' / 'apps'
    ADJANGO_APPS_PREPATH = 'apps.'  # if apps in BASE_DIR/apps/app1,app2...
    # ADJANGO_APPS_PREPATH = None # if in BASE_DIR/app1,app2...
    ADJANGO_EXCEPTION_REPORT_EMAIL = ('ivanhvalevskey@gmail.com',)
    # Template for sending a email report on an uncaught error.
    # Вы можете его переопределить он принимает лишь context={'traceback': 'str'}
    ADJANGO_EXCEPTION_REPORT_TEMPLATE = 'logui/error_report.html'
    
    # adjango использует send_emails для отправки писем синхронно.
    ADJANGO_USE_CELERY_MAIL_REPORT = True  # Использовать ли celery для отправки писем
    ADJANGO_CELERY_SEND_MAIL_TASK = send_mail_task_function  # callable task
    ADJANGO_LOGGER_NAME = 'global'
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
