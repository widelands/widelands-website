# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime
from django.conf import settings
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, verbose_name='Title')),
                ('content', models.TextField(verbose_name='Content')),
                ('summary', models.CharField(max_length=150,
                                             null=True, verbose_name='Summary', blank=True)),
                ('markup', models.CharField(blank=True, max_length=3, null=True, verbose_name='Content Markup', choices=[
                 (b'crl', 'Creole'), (b'rst', 'reStructuredText'), (b'txl', 'Textile'), (b'mrk', 'Markdown')])),
                ('creator_ip', models.GenericIPAddressField(
                    null=True, verbose_name='IP Address of the Article Creator', blank=True)),
                ('created_at', models.DateTimeField(
                    default=datetime.datetime.now)),
                ('last_update', models.DateTimeField(null=True, blank=True)),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('tags', tagging.fields.TagField(max_length=255, blank=True)),
                ('content_type', models.ForeignKey(
                    to='contenttypes.ContentType', null=True)),
                ('creator', models.ForeignKey(verbose_name='Article Creator',
                                              to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
            },
        ),
        migrations.CreateModel(
            name='ChangeSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('editor_ip', models.GenericIPAddressField(
                    verbose_name='IP Address of the Editor')),
                ('revision', models.IntegerField(verbose_name='Revision Number')),
                ('old_title', models.CharField(max_length=50,
                                               verbose_name='Old Title', blank=True)),
                ('old_markup', models.CharField(blank=True, max_length=3, null=True, verbose_name='Article Content Markup', choices=[
                 (b'crl', 'Creole'), (b'rst', 'reStructuredText'), (b'txl', 'Textile'), (b'mrk', 'Markdown')])),
                ('content_diff', models.TextField(
                    verbose_name='Content Patch', blank=True)),
                ('comment', models.TextField(
                    verbose_name='Editor comment', blank=True)),
                ('modified', models.DateTimeField(
                    default=datetime.datetime.now, verbose_name='Modified at')),
                ('reverted', models.BooleanField(
                    default=False, verbose_name='Reverted Revision')),
                ('article', models.ForeignKey(
                    verbose_name='Article', to='wiki.Article')),
                ('editor', models.ForeignKey(verbose_name='Editor',
                                             to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-revision',),
                'get_latest_by': 'modified',
                'verbose_name': 'Change set',
                'verbose_name_plural': 'Change sets',
            },
        ),
    ]
