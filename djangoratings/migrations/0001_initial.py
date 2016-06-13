# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='IgnoredObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('key', models.CharField(max_length=32)),
                ('score', models.IntegerField()),
                ('votes', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='SimilarUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('agrees', models.PositiveIntegerField(default=0)),
                ('disagrees', models.PositiveIntegerField(default=0)),
                ('exclude', models.BooleanField(default=False)),
                ('from_user', models.ForeignKey(related_name='similar_users', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(related_name='similar_users_from', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('key', models.CharField(max_length=32)),
                ('score', models.IntegerField()),
                ('ip_address', models.GenericIPAddressField()),
                ('cookie', models.CharField(max_length=32, null=True, blank=True)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('date_changed', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('content_type', models.ForeignKey(related_name='votes', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(related_name='votes', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('content_type', 'object_id', 'key', 'user', 'ip_address', 'cookie')]),
        ),
        migrations.AlterUniqueTogether(
            name='similaruser',
            unique_together=set([('from_user', 'to_user')]),
        ),
        migrations.AlterUniqueTogether(
            name='score',
            unique_together=set([('content_type', 'object_id', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='ignoredobject',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
