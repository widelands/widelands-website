# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ("wlggz", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ggzauth",
            name="confirmed",
        ),
        migrations.RemoveField(
            model_name="ggzauth",
            name="lastlogin",
        ),
    ]
