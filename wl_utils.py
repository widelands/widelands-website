
def get_real_ip(request):
    """Returns the real user IP, even if behind a proxy."""
    for key in ('HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR'):
        if key in request.META:
            return request.META[key]

    return '192.168.255.255'
