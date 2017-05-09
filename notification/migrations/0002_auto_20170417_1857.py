# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notice',
            name='notice_type',
        ),
        migrations.RemoveField(
            model_name='notice',
            name='user',
        ),
        migrations.DeleteModel(
            name='Notice',
        ),
    ]
