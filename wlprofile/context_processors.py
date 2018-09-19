from django.conf import settings


def deleted_user_data(request):
    context = {'DELETED_USERNAME': settings.DELETED_USERNAME}
    return context
