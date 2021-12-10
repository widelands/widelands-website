from django.shortcuts import render
from wladdons_settings.models import get_addon_setting
from wladdons_settings.settings import ADDONNOTICETYPES
from django.contrib.auth.decorators import login_required


@login_required
def addon_settings(request):
    settings = []

    for label in ADDONNOTICETYPES:
        setting = get_addon_setting(request.user, label)
        if request.method == 'POST':
            if request.POST.get(label) == 'on':
                setting.shouldsend = True
            else:
                setting.shouldsend = False
            setting.save()
        settings.append(setting)

    return render(request, 'wladdons_settings/settings.html', {
        'objects': settings})
