# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SuspiciousInput',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=200, verbose_name=b'suspicious user input')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(verbose_name=b'related model', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(verbose_name=b'related user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['content_type_id'],
                'default_permissions': ('change', 'delete'),
            },
        ),
    ]
