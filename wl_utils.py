from django.conf import settings

def get_real_ip(request):
    """ Returns the real user IP, even if behind a proxy.
    Set BEHIND_PROXY to True in your settings if Django is
    running behind a proxy.
    """
    print('franku: Funktioniert')
    if getattr(settings, 'BEHIND_PROXY', False):
        return request.META['HTTP_X_FORWARDED_FOR']
    return request.META['REMOTE_ADDR']
