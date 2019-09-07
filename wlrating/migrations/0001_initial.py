# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='season',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(default=0)),
                ('end_date', models.DateTimeField(default=0)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(default=0, verbose_name=b'one hour of availability')),
                ('game_type', models.IntegerField()),
                ('game_map', models.CharField(max_length=255)),
                ('win_team',  models.IntegerField()),
                ('game_status',  models.IntegerField()),
                ('game_breaks', models.IntegerField()),
                ('counted_in_score', models.BooleanField(default=False))
            ],
        ),
        migrations.CreateModel(
            name='temporary_user',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=255, blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(to='temporary_user')),
                ('game', models.ForeignKey(to='game')),
                ('team', models.IntegerField()),
                ('submitter', models.BooleanField(default=False)),
                ('tribe', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='player_rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(to='temporary_user')),
                ('rating_type', models.IntegerField()),
                ('decimal1', models.DecimalField(max_digits=10, decimal_places=5)),
                ('decimal2', models.DecimalField(max_digits=10, decimal_places=5)), 
                ('decimal3', models.DecimalField(max_digits=10, decimal_places=5)), 
                ('season', models.ForeignKey(to='season')),
            ],
        ),
    ]
