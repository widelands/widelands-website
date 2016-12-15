from django.conf import settings
from pybb.models import Forum


def settings_for_templates(request):
    context = {'USE_GOOGLE_ANALYTICS': settings.USE_GOOGLE_ANALYTICS,
               'LOGO_FILE': settings.LOGO_FILE}
    return context


def forums_navigation(request):
    """Make the forums available to all contexts.

    Ordering inside each forum category is made by the field 'position' of pybb.forum.

    """
    forums = Forum.objects.all()
    return {'forums': forums}
