from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from collections import OrderedDict
from notification.models import NoticeType, NOTICE_MEDIA, get_notification_setting


@login_required
def notice_settings(request):
    app_tables = {}
    for notice_type in NoticeType.objects.all().order_by("label"):
        # Assuming each notice_type.label begins with the name of the app
        # followed by an underscore:
        app = notice_type.label.partition("_")[0]
        app_tables.setdefault(app, [])
        checkbox_values = []
        for medium_id, medium_display in NOTICE_MEDIA:
            form_label = f"{notice_type.label}_{medium_id}"
            setting = get_notification_setting(request.user, notice_type, medium_id)
            if request.method == "POST":
                if request.POST.get(form_label) == "on":
                    setting.send = True
                else:
                    setting.send = False
                setting.save()
            checkbox_values.append((form_label, setting.send))

        app_tables[app].append(
            {"notice_type": notice_type, "html_values": checkbox_values}
        )

    return render(
        request,
        "notification/notice_settings.html",
        {
            "column_headers": [
                medium_display for medium_id, medium_display in NOTICE_MEDIA
            ],
            "app_tables": OrderedDict(
                sorted(list(app_tables.items()), key=lambda t: t[0])
            ),
        },
    )
