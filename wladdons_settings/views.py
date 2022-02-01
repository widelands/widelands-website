from django.shortcuts import render
from wladdons_settings.models import AddonNoticeType
from wladdons_settings.models import get_addon_usersetting
from wladdons_settings.models import get_addons_for_user

from django.contrib.auth.decorators import login_required


@login_required
def addon_settings(request):
    settings = []
    addons = []
    author_related_settings = []

    notices = AddonNoticeType.objects.all()

    for notice in notices:
        usersetting = get_addon_usersetting(request.user, notice)
        if usersetting is not None:
            if request.method == 'POST':
                if request.POST.get(usersetting.notice_type.slug) == 'on':
                    usersetting.shouldsend = True
                else:
                    usersetting.shouldsend = False
                usersetting.save()
            if usersetting.author_related:
                author_related_settings.append(usersetting)
            else:
                settings.append(usersetting)
    
    addons = get_addons_for_user(request.user.pk)
    return render(request, 'wladdons_settings/settings.html', {
        'addon_settings': settings,
        'addons': addons,
        'author_related_settings': author_related_settings,
        })
