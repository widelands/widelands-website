# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ("wlimages", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="image",
            name="url",
        ),
    ]
