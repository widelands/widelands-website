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
            name='hided',
            field=models.BooleanField(default=False, verbose_name='Hided'),
        ),
        migrations.AddField(
            model_name='topic',
            name='hided',
            field=models.BooleanField(default=False, verbose_name='Hided'),
        ),
    ]
