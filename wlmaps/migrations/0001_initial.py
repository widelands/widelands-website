# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('slug', models.SlugField(unique=True)),
                ('author', models.CharField(max_length=255)),
                ('w', models.PositiveIntegerField(verbose_name=b'Width')),
                ('h', models.PositiveIntegerField(verbose_name=b'Height')),
                ('nr_players', models.PositiveIntegerField(
                    verbose_name=b'Max Players')),
                ('descr', models.TextField(verbose_name=b'Description')),
                ('hint', models.TextField(verbose_name=b'Hint')),
                ('minimap', models.ImageField(
                    upload_to=b'wlmaps/minimaps', verbose_name=b'Minimap')),
                ('file', models.FileField(
                    upload_to=b'wlmaps/maps', verbose_name=b'Mapfile')),
                ('world_name', models.CharField(max_length=50)),
                ('pub_date', models.DateTimeField(default=datetime.datetime.now)),
                ('uploader_comment', models.TextField(
                    verbose_name=b'Uploader comment', blank=True)),
                ('nr_downloads', models.PositiveIntegerField(
                    default=0, verbose_name=b'Download count')),
                ('rating_votes', models.PositiveIntegerField(
                    default=0, editable=False, blank=True)),
                ('rating_score', models.IntegerField(
                    default=0, editable=False, blank=True)),
                ('uploader', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-pub_date',),
                'get_latest_by': 'pub_date',
            },
        ),
    ]
