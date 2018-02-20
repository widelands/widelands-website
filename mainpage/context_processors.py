from django.conf import settings


def settings_for_templates(request):
    context = {'USE_GOOGLE_ANALYTICS': settings.USE_GOOGLE_ANALYTICS,}
    return context
