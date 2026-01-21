from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware for adding additional security headers
    """

    @staticmethod
    def process_response(request, response: HttpResponse) -> HttpResponse:
        # Content Security Policy for API and media files
        if request.path.startswith('/api/') or request.path.startswith('/media/'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "img-src 'self' data: https:; "
                "script-src 'none'; "
                "style-src 'self' 'unsafe-inline'; "
                "object-src 'none'; "
                "frame-ancestors 'none'"
            )

        # Ensure HTTPS for media files URLs in production
        if not settings.DEBUG and request.path.startswith('/media/'):
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        # Prevent MIME sniffing
        response['X-Content-Type-Options'] = 'nosniff'

        # Prevent clickjacking
        # Don't set DENY for admin so Django can use X_FRAME_OPTIONS = 'SAMEORIGIN'
        # for iframe modal windows
        admin_path = getattr(settings, 'ADJANGO_ADMIN_PATH', '/admin/')
        if not request.path.startswith(admin_path):
            response['X-Frame-Options'] = 'DENY'

        # XSS Protection
        response['X-XSS-Protection'] = '1; mode=block'

        return response


class ForceHTTPSMiddleware(MiddlewareMixin):
    """
    Middleware for forcing HTTPS redirect in production
    """

    @staticmethod
    def process_request(request):
        if not settings.DEBUG:
            # Check proxy headers (nginx, CloudFlare, etc.)
            forwarded_proto = request.META.get('HTTP_X_FORWARDED_PROTO')
            forwarded_ssl = request.META.get('HTTP_X_FORWARDED_SSL')

            # If request came via HTTP, redirect to HTTPS
            if (
                (forwarded_proto and forwarded_proto.lower() != 'https')
                or (forwarded_ssl and forwarded_ssl.lower() != 'on')
                or (not forwarded_proto and not forwarded_ssl and not request.is_secure())
            ):
                # Build HTTPS URL
                https_url = f"https://{request.get_host()}{request.get_full_path()}"

                from django.http import HttpResponsePermanentRedirect

                return HttpResponsePermanentRedirect(https_url)

        return None
