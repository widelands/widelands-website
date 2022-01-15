from django.shortcuts import render
from wladdons_settings.models import AddonNoticeType
from wladdons_settings.models import get_addon_usersetting
from django.contrib.auth.decorators import login_required


@login_required
def addon_settings(request):
    settings = []

    notices = AddonNoticeType.objects.all()

    for notice in notices:
        usersetting = get_addon_usersetting(request.user, notice)
        if request.method == 'POST':
            if request.POST.get(usersetting.notice_type.label) == 'on':
                usersetting.shouldsend = True
            else:
                usersetting.shouldsend = False
            usersetting.save()
        settings.append(usersetting)

    return render(request, 'wladdons_settings/settings.html', {
        'objects': settings})
