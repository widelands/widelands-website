from django.conf import settings


def deleted_email_address(request):
    context = { 'DELETED_EMAIL_ADDRESS': settings.DELETED_MAIL_ADDRESS}
    return context