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
    ADJANGO_BACKENDS_APPS = BASE_DIR / 'apps'
    ADJANGO_FRONTEND_APPS = BASE_DIR.parent / 'frontend' / 'src' / 'apps'
    ADJANGO_APPS_PREPATH = 'apps.'
    ADJANGO_EXCEPTION_REPORT_EMAIL = ('ivanhvalevskey@gmail.com',)
    ADJANGO_EXCEPTION_REPORT_TEMPLATE = 'core/error_report.html'
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
