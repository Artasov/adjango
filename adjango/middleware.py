# middleware.py
import json
import logging

from django.conf import settings

from adjango.conf import ADJANGO_IP_LOGGER, ADJANGO_IP_META_NAME, MEDIA_SUBSTITUTION_URL, ADJANGO_BASE_LOGGER


class IPAddressMiddleware:
    """
    Позволяет легко получать IP-адрес через `request.ip`.
    settings.ADJANGO_IP_META_NAME - название HTTP-заголовка, содержащего IP-адрес
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        log = logging.getLogger(ADJANGO_IP_LOGGER) if ADJANGO_IP_LOGGER else None
        if log:
            log.warning(f"{request.META.get('HTTP_X_FORWARDED_FOR')} HTTP_X_FORWARDED_FOR")
            log.warning(f"{request.META.get('HTTP_X_REAL_IP')} HTTP_X_REAL_IP")
            log.warning(f"{request.META.get('REMOTE_ADDR')} REMOTE_ADDR")
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            request.ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
        elif request.META.get("HTTP_X_REAL_IP"):
            request.ip = request.META.get("HTTP_X_REAL_IP")
        elif request.META.get("REMOTE_ADDR"):
            request.ip = request.META.get("REMOTE_ADDR")
        else:
            request.ip = None
        if ADJANGO_IP_META_NAME:
            if request.META.get(ADJANGO_IP_META_NAME):
                if ADJANGO_IP_META_NAME == 'HTTP_X_FORWARDED_FOR':
                    _ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
                else:
                    _ip = request.META.get(ADJANGO_IP_META_NAME)
                request.META['REMOTE_ADDR'] = _ip
                request.ip = _ip
        return self.get_response(request)


class MediaDomainSubstitutionJSONMiddleware:
    """
    Middleware для подмены домена в JSON-ответах.
    Если какое-либо строковое значение начинается с settings.MEDIA_URL,
    оно заменяется на settings.MEDIA_SUBSTITUTION_URL + оригинальный путь.

    Например, если:
        MEDIA_URL = '/media/'
        MEDIA_SUBSTITUTION_URL = 'https://media.example.com'
    То строка "/media/user/images/avatar/x.jpg"
    будет заменена на "https://media.example.com/media/user/images/avatar/x.jpg"

    P.s. очевидно этот пересчет - излишняя нагрузка,
        но для локальной разработки и доступа к серверной статике гуд.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.media_url = getattr(settings, 'MEDIA_URL', '')
        self.media_domain = MEDIA_SUBSTITUTION_URL
        self.log = logging.getLogger(ADJANGO_BASE_LOGGER) if ADJANGO_BASE_LOGGER else None

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get('Content-Type', '')
        if not self.media_domain:
            raise ValueError('settings.MEDIA_SUBSTITUTION_URL = "https://XXX.com" not specified')
        if 'application/json' in content_type and response.content:
            try:
                charset = response.charset if hasattr(response, 'charset') else 'utf-8'
                original_content = response.content.decode(charset)
                data = json.loads(original_content)
                new_data = self._replace_media_urls(data)
                new_content = json.dumps(new_data)
                response.content = new_content.encode(charset)
                response['Content-Length'] = len(response.content)
            except Exception as e:
                if self.log: self.log.exception('Error in MediaDomainSubstitutionJSONMiddleware: %s', e)
        return response

    def _replace_media_urls(self, data):
        if isinstance(data, dict):
            return {k: self._replace_media_urls(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_media_urls(item) for item in data]
        elif isinstance(data, str):
            if self.media_domain and self.media_url and data.startswith(self.media_url):
                return f'{self.media_domain}{data}'
            return data
        return data
