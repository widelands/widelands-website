# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pybb', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='Hidden'),
        ),
    ]
