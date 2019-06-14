# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings
import mainpage.wl_utils as wl_utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GGZAuth',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(default=b'', max_length=80,
                                              verbose_name='ggz password', blank=True)),
                ('lastlogin', models.DateTimeField(
                    null=True, verbose_name='ggz lastlogin')),
                ('permissions', models.IntegerField(
                    default=7, verbose_name='ggz permissions')),
                ('confirmed', models.IntegerField(default=1,
                                                  verbose_name='confirmed', editable=False)),
                ('user', wl_utils.AutoOneToOneField(related_name='wlggz',
                                                    verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'ggz',
                'verbose_name_plural': 'ggz',
            },
        ),
    ]
