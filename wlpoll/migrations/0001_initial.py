# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime
from django.conf import settings
import wlpoll.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.CharField(max_length=256)),
                ('votes', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('pub_date', models.DateTimeField(
                    default=datetime.datetime.now, verbose_name=b'date published')),
                ('closed_date', models.DateTimeField(default=wlpoll.models.closed_date_default,
                                                     null=True, verbose_name=b'date closed', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('date_voted', models.DateTimeField(
                    default=datetime.datetime.now, verbose_name=b'voted at')),
                ('choice', models.ForeignKey(to='wlpoll.Choice', on_delete=models.CASCADE)),
                ('poll', models.ForeignKey(to='wlpoll.Poll', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(
                    related_name='poll_votes', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='choice',
            name='poll',
            field=models.ForeignKey(related_name='choices', to='wlpoll.Poll', on_delete=models.CASCADE),
        ),
    ]
