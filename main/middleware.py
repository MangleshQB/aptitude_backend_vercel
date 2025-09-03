from django.http import HttpResponseForbidden
from django.conf import settings

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

import ipaddress

def is_ip_in_allowed_range(client_ip, allowed_hosts):
    for host in allowed_hosts:
        if '/' in host:
            if ipaddress.ip_address(client_ip) in ipaddress.ip_network(host):
                return True
        elif client_ip == host:
            return True
    return False


class RestrictIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_ip = get_client_ip(request)
        if not is_ip_in_allowed_range(client_ip, settings.ALLOWED_HOSTS):
            return HttpResponseForbidden("Access denied: Your IP is not allowed.")
        return self.get_response(request)
