# middleware.py
class IPAddressMiddleware:
    """
    Позволяет легко получать IP-адрес через `request.ip`.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            request.ip = request.META.get('HTTP_X_FORWARDED_FOR')
        elif request.META.get("HTTP_X_REAL_IP"):
            request.ip = request.META.get("HTTP_X_REAL_IP")
        elif request.META.get("REMOTE_ADDR"):
            request.ip = request.META.get("REMOTE_ADDR")
        else:
            request.ip = None
        return self.get_response(request)
