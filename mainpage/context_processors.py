from django.conf import settings

# Make some variables available in each context (template)

def settings_for_templates(request):
    context = {'USE_GOOGLE_ANALYTICS': settings.USE_GOOGLE_ANALYTICS,
               'LOGO_FILE': settings.LOGO_FILE}
    return context
