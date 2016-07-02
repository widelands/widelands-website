# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import wlprofile.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site', models.URLField(default=b'', verbose_name='Website', blank=True)),
                ('jabber', models.CharField(default=b'', max_length=80, verbose_name='Jabber', blank=True)),
                ('icq', models.CharField(default=b'', max_length=12, verbose_name='ICQ', blank=True)),
                ('msn', models.CharField(default=b'', max_length=80, verbose_name='MSN', blank=True)),
                ('aim', models.CharField(default=b'', max_length=80, verbose_name='AIM', blank=True)),
                ('yahoo', models.CharField(default=b'', max_length=80, verbose_name='Yahoo', blank=True)),
                ('location', models.CharField(default=b'', max_length=30, verbose_name='Location', blank=True)),
                ('time_zone', models.FloatField(default=3.0, verbose_name='Time zone', choices=[(-12.0, b'-12'), (-11.0, b'-11'), (-10.0, b'-10'), (-9.5, b'-09.5'), (-9.0, b'-09'), (-8.5, b'-08.5'), (-8.0, b'-08 PST'), (-7.0, b'-07 MST'), (-6.0, b'-06 CST'), (-5.0, b'-05 EST'), (-4.0, b'-04 AST'), (-3.5, b'-03.5'), (-3.0, b'-03 ADT'), (-2.0, b'-02'), (-1.0, b'-01'), (0.0, b'00 GMT'), (1.0, b'+01 CET'), (2.0, b'+02'), (3.0, b'+03'), (3.5, b'+03.5'), (4.0, b'+04'), (4.5, b'+04.5'), (5.0, b'+05'), (5.5, b'+05.5'), (6.0, b'+06'), (6.5, b'+06.5'), (7.0, b'+07'), (8.0, b'+08'), (9.0, b'+09'), (9.5, b'+09.5'), (10.0, b'+10'), (10.5, b'+10.5'), (11.0, b'+11'), (11.5, b'+11.5'), (12.0, b'+12'), (13.0, b'+13'), (14.0, b'+14')])),
                ('time_display', models.CharField(default=b'%ND(Y-m-d,) H:i', max_length=80, verbose_name='Time display')),
                ('signature', models.TextField(default=b'', max_length=255, verbose_name='Signature', blank=True)),
                ('avatar', wlprofile.fields.ExtendedImageField(default=b'wlprofile/anonymous.png', upload_to=b'wlprofile/avatars/', verbose_name='Avatar', blank=True)),
                ('show_signatures', models.BooleanField(default=True, verbose_name='Show signatures')),
                ('user', wlprofile.fields.AutoOneToOneField(related_name='wlprofile', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
        ),
    ]
