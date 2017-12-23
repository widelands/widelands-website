# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Availabilities',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('avail_time', models.DateTimeField(default=0, verbose_name=b'one hour of availability')),
                ('user', models.ForeignKey(related_name='availabilities', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
