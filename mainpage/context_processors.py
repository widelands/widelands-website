from django.conf import settings


def settings_for_templates(request):
    context = {'USE_GOOGLE_ANALYTICS': settings.USE_GOOGLE_ANALYTICS,}
    return context

def deleted_email_address(request):
    context = { 'deleted_email_address': settings.DELETED_MAIL_ADDRESS}
    return context