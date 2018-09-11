from django.conf import settings


def deleted_user_data(request):
    context = {'DELETED_MAIL_ADDRESS': settings.DELETED_MAIL_ADDRESS,
               'DELETED_USERNAME': settings.DELETED_USERNAME}
    return context
