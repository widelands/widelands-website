from django.conf import settings

def settings_for_templates(request):
    return {'USE_GOOGLE_ANALYTICS': settings.USE_GOOGLE_ANALYTICS}
