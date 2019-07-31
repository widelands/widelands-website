# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(default=0, verbose_name=b'one hour of availability')),
                ('user', models.ForeignKey(related_name='rating', to=settings.AUTH_USER_MODEL)),
                ('game_type', models.CharField(max_length=255)),
                ('game_map', models.CharField(max_length=255)),
                ('players', models.CharField(max_length=255)),
                ('result', models.CharField(max_length=255)),
                ('submitter', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('player', models.CharField(max_length=255)),
                ('rating', models.DecimalField(max_digits=10, decimal_places=2)),
                ('standard_deviation', models.DecimalField(max_digits=10, decimal_places=2)),
                ('volatility', models.DecimalField(max_digits=10, decimal_places=5)),
            ],
        ),
    ]
