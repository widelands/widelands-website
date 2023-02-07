# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings
import news.models

# import tagging.fields


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
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
                ("title", models.CharField(max_length=100, verbose_name="title")),
                ("slug", models.SlugField(unique=True, verbose_name="slug")),
                ("image", models.ImageField(upload_to=news.models.get_upload_name)),
            ],
            options={
                "ordering": ("title",),
                "db_table": "news_categories",
                "verbose_name": "category",
                "verbose_name_plural": "categories",
            },
        ),
        migrations.CreateModel(
            name="Post",
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
                ("title", models.CharField(max_length=200, verbose_name="title")),
                (
                    "slug",
                    models.SlugField(verbose_name="slug", unique_for_date=b"publish"),
                ),
                ("body", models.TextField(verbose_name="body")),
                ("tease", models.TextField(verbose_name="tease", blank=True)),
                (
                    "status",
                    models.IntegerField(
                        default=2,
                        verbose_name="status",
                        choices=[(1, "Draft"), (2, "Public")],
                    ),
                ),
                (
                    "allow_comments",
                    models.BooleanField(default=True, verbose_name="allow comments"),
                ),
                ("publish", models.DateTimeField(verbose_name="publish")),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="created"),
                ),
                (
                    "modified",
                    models.DateTimeField(auto_now=True, verbose_name="modified"),
                ),
                #                ("tags", tagging.fields.TagField(max_length=255, blank=True)),
                (
                    "author",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE
                    ),
                ),
                ("categories", models.ManyToManyField(to="news.Category", blank=True)),
            ],
            options={
                "ordering": ("-publish",),
                "db_table": "news_posts",
                "verbose_name": "post",
                "verbose_name_plural": "posts",
                "get_latest_by": "publish",
            },
        ),
    ]
