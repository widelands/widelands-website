# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('size', models.IntegerField(verbose_name='Size')),
                ('content_type', models.CharField(
                    max_length=255, verbose_name='Content type')),
                ('path', models.CharField(max_length=255, verbose_name='Path')),
                ('name', models.TextField(verbose_name='Name')),
                ('hash', models.CharField(default=b'', max_length=40,
                                          verbose_name='Hash', db_index=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80, verbose_name='Name')),
                ('position', models.IntegerField(
                    default=0, verbose_name='Position', blank=True)),
            ],
            options={
                'ordering': ['position'],
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80, verbose_name='Name')),
                ('position', models.IntegerField(
                    default=0, verbose_name='Position', blank=True)),
                ('description', models.TextField(default=b'',
                                                 verbose_name='Description', blank=True)),
                ('updated', models.DateTimeField(
                    null=True, verbose_name='Updated')),
                ('category', models.ForeignKey(related_name='forums',
                                               verbose_name='Category', to='pybb.Category', on_delete=models.CASCADE)),
                ('moderators', models.ManyToManyField(
                    to=settings.AUTH_USER_MODEL, verbose_name='Moderators', blank=True)),
            ],
            options={
                'ordering': ['position'],
                'verbose_name': 'Forum',
                'verbose_name_plural': 'Forums',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(
                    verbose_name='Created', blank=True)),
                ('updated', models.DateTimeField(
                    null=True, verbose_name='Updated', blank=True)),
                ('markup', models.CharField(default=b'markdown', max_length=15, verbose_name='Markup', choices=[
                 (b'markdown', b'markdown'), (b'bbcode', b'bbcode')])),
                ('body', models.TextField(verbose_name='Message')),
                ('body_html', models.TextField(verbose_name='HTML version')),
                ('body_text', models.TextField(verbose_name='Text version')),
                ('user_ip', models.GenericIPAddressField(
                    default=b'', verbose_name='User IP')),
            ],
            options={
                'ordering': ['created'],
                'verbose_name': 'Post',
                'verbose_name_plural': 'Posts',
            },
        ),
        migrations.CreateModel(
            name='PrivateMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('read', models.BooleanField(default=False, verbose_name='Read')),
                ('created', models.DateTimeField(
                    verbose_name='Created', blank=True)),
                ('markup', models.CharField(default=b'markdown', max_length=15, verbose_name='Markup', choices=[
                 (b'markdown', b'markdown'), (b'bbcode', b'bbcode')])),
                ('subject', models.CharField(max_length=255, verbose_name='Subject')),
                ('body', models.TextField(verbose_name='Message')),
                ('body_html', models.TextField(verbose_name='HTML version')),
                ('body_text', models.TextField(verbose_name='Text version')),
                ('dst_user', models.ForeignKey(related_name='dst_users',
                                               verbose_name='Recipient', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('src_user', models.ForeignKey(related_name='src_users',
                                               verbose_name='Author', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-created'],
                'verbose_name': 'Private message',
                'verbose_name_plural': 'Private messages',
            },
        ),
        migrations.CreateModel(
            name='Read',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(verbose_name='Time', blank=True)),
            ],
            options={
                'verbose_name': 'Read',
                'verbose_name_plural': 'Reads',
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Subject')),
                ('created', models.DateTimeField(
                    null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(
                    null=True, verbose_name='Updated')),
                ('views', models.IntegerField(default=0,
                                              verbose_name='Views count', blank=True)),
                ('sticky', models.BooleanField(default=False, verbose_name='Sticky')),
                ('closed', models.BooleanField(default=False, verbose_name='Closed')),
                ('forum', models.ForeignKey(related_name='topics',
                                            verbose_name='Forum', to='pybb.Forum', on_delete=models.CASCADE)),
                ('subscribers', models.ManyToManyField(related_name='subscriptions',
                                                       verbose_name='Subscribers', to=settings.AUTH_USER_MODEL, blank=True)),
                ('user', models.ForeignKey(
                    verbose_name='User', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-updated'],
                'verbose_name': 'Topic',
                'verbose_name_plural': 'Topics',
            },
        ),
        migrations.AddField(
            model_name='read',
            name='topic',
            field=models.ForeignKey(verbose_name='Topic', to='pybb.Topic', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='read',
            name='user',
            field=models.ForeignKey(
                verbose_name='User', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='post',
            name='topic',
            field=models.ForeignKey(
                related_name='posts', verbose_name='Topic', to='pybb.Topic', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.ForeignKey(
                related_name='posts', verbose_name='User', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='attachment',
            name='post',
            field=models.ForeignKey(
                related_name='attachments', verbose_name='Post', to='pybb.Post', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='read',
            unique_together=set([('user', 'topic')]),
        ),
    ]
