# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Image",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
                ("name", models.CharField(max_length=100)),
                ("revision", models.PositiveIntegerField()),
                (
                    "editor_ip",
                    models.GenericIPAddressField(
                        null=True, verbose_name="IP address", blank=True
                    ),
                ),
                (
                    "date_submitted",
                    models.DateTimeField(
                        default=datetime.datetime.now,
                        verbose_name="date/time submitted",
                    ),
                ),
                ("image", models.ImageField(upload_to=b"wlimages/")),
                ("url", models.CharField(max_length=250)),
                (
                    "content_type",
                    models.ForeignKey(
                        to="contenttypes.ContentType", on_delete=models.CASCADE
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
            options={
                "ordering": ("-date_submitted",),
                "get_latest_by": "date_submitted",
                "verbose_name": "Image",
                "verbose_name_plural": "Images",
            },
        ),
    ]
