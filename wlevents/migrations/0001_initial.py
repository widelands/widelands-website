# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('link', models.CharField(max_length=1024)),
                ('start_date', models.DateField(verbose_name=b'start date')),
                ('end_date', models.DateField(null=True,
                                              verbose_name=b'end date', blank=True)),
            ],
        ),
    ]
