from ipaddress import ip_address, ip_network

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class RealIPFromForwardedForMiddleware(MiddlewareMixin):
    """
    Sets real IP in request.META['REMOTE_ADDR'] from proxy headers
    (X-Forwarded-For / X-Real-IP) for requests coming from trusted
    proxies (Docker/overlay/local networks).

    This is important for correct DRF throttling, logging, and any
    mechanisms that depend on IP address.
    """

    # Default trusted proxy ranges (Docker/local networks)
    DEFAULT_TRUSTED_CIDRS: tuple[str, ...] = (
        '10.0.0.0/8',
        '172.16.0.0/12',
        '192.168.0.0/16',
        '127.0.0.1/32',
        '::1/128',
    )

    @classmethod
    def _trusted_networks(cls):
        cidrs = getattr(settings, 'TRUSTED_PROXY_CIDRS', cls.DEFAULT_TRUSTED_CIDRS)
        return tuple(ip_network(c) for c in cidrs)

    @classmethod
    def _is_from_trusted_proxy(cls, remote: str | None) -> bool:
        if not remote:
            return False
        try:
            rip = ip_address(remote.split(':')[0])  # in case of IPv6 with port
        except ValueError:
            return False
        return any(rip in net for net in cls._trusted_networks())

    def process_request(self, request):
        remote = request.META.get('REMOTE_ADDR')
        if not self._is_from_trusted_proxy(remote):
            return None

        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            # Take the leftmost IP - this is the real client
            real_ip = xff.split(',')[0].strip()
            if real_ip:
                request.META['REMOTE_ADDR_ORIGINAL'] = remote
                request.META['REMOTE_ADDR'] = real_ip
                return None

        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip:
            request.META['REMOTE_ADDR_ORIGINAL'] = remote
            request.META['REMOTE_ADDR'] = x_real_ip.strip()
        return None
