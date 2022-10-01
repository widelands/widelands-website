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
            name="FreeThreadedComment",
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
                ("object_id", models.PositiveIntegerField(verbose_name="object ID")),
                ("name", models.CharField(max_length=128, verbose_name="name")),
                ("website", models.URLField(verbose_name="site", blank=True)),
                (
                    "email",
                    models.EmailField(
                        max_length=254, verbose_name="e-mail address", blank=True
                    ),
                ),
                (
                    "date_submitted",
                    models.DateTimeField(
                        default=datetime.datetime.now,
                        verbose_name="date/time submitted",
                    ),
                ),
                (
                    "date_modified",
                    models.DateTimeField(
                        default=datetime.datetime.now, verbose_name="date/time modified"
                    ),
                ),
                (
                    "date_approved",
                    models.DateTimeField(
                        default=None,
                        null=True,
                        verbose_name="date/time approved",
                        blank=True,
                    ),
                ),
                ("comment", models.TextField(verbose_name="comment")),
                (
                    "markup",
                    models.IntegerField(
                        default=b"markdown",
                        null=True,
                        blank=True,
                        choices=[
                            (1, "markdown"),
                            (2, "textile"),
                            (3, "restructuredtext"),
                            (5, "plaintext"),
                        ],
                    ),
                ),
                (
                    "is_public",
                    models.BooleanField(default=True, verbose_name="is public"),
                ),
                (
                    "is_approved",
                    models.BooleanField(default=False, verbose_name="is approved"),
                ),
                (
                    "ip_address",
                    models.GenericIPAddressField(
                        null=True, verbose_name="IP address", blank=True
                    ),
                ),
                ("content_type", models.ForeignKey(to="contenttypes.ContentType")),
                (
                    "parent",
                    models.ForeignKey(
                        related_name="children",
                        default=None,
                        blank=True,
                        to="threadedcomments.FreeThreadedComment",
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("-date_submitted",),
                "get_latest_by": "date_submitted",
                "verbose_name": "Free Threaded Comment",
                "verbose_name_plural": "Free Threaded Comments",
            },
        ),
        migrations.CreateModel(
            name="TestModel",
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
                ("name", models.CharField(max_length=5)),
                ("is_public", models.BooleanField(default=True)),
                ("date", models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name="ThreadedComment",
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
                ("object_id", models.PositiveIntegerField(verbose_name="object ID")),
                (
                    "date_submitted",
                    models.DateTimeField(
                        default=datetime.datetime.now,
                        verbose_name="date/time submitted",
                    ),
                ),
                (
                    "date_modified",
                    models.DateTimeField(
                        default=datetime.datetime.now, verbose_name="date/time modified"
                    ),
                ),
                (
                    "date_approved",
                    models.DateTimeField(
                        default=None,
                        null=True,
                        verbose_name="date/time approved",
                        blank=True,
                    ),
                ),
                ("comment", models.TextField(verbose_name="comment")),
                (
                    "markup",
                    models.IntegerField(
                        default=b"markdown",
                        null=True,
                        blank=True,
                        choices=[
                            (1, "markdown"),
                            (2, "textile"),
                            (3, "restructuredtext"),
                            (5, "plaintext"),
                        ],
                    ),
                ),
                (
                    "is_public",
                    models.BooleanField(default=True, verbose_name="is public"),
                ),
                (
                    "is_approved",
                    models.BooleanField(default=False, verbose_name="is approved"),
                ),
                (
                    "ip_address",
                    models.GenericIPAddressField(
                        null=True, verbose_name="IP address", blank=True
                    ),
                ),
                ("content_type", models.ForeignKey(to="contenttypes.ContentType")),
                (
                    "parent",
                    models.ForeignKey(
                        related_name="children",
                        default=None,
                        blank=True,
                        to="threadedcomments.ThreadedComment",
                        null=True,
                    ),
                ),
                ("user", models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-date_submitted",),
                "get_latest_by": "date_submitted",
                "verbose_name": "Threaded Comment",
                "verbose_name_plural": "Threaded Comments",
            },
        ),
    ]
