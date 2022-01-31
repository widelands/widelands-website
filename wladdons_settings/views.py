from django.shortcuts import render
from wladdons_settings.models import AddonNoticeType
from wladdons_settings.models import get_addon_usersetting
from wladdons_settings.models import get_addons_for_user

from django.contrib.auth.decorators import login_required


@login_required
def addon_settings(request):
    settings = []
    addons = []

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
            settings.append(usersetting)

    # Split the list
    add_related=[settings.pop(i) for i, x in enumerate(settings) if x.author_related]
    
    addons = get_addons_for_user(request.user.pk)
    return render(request, 'wladdons_settings/settings.html', {
        'addon_settings': settings,
        'addons': addons,
        'author_related_settings': add_related,
        })
