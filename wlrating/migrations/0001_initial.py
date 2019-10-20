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
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(default=0)),
                ('end_date', models.DateTimeField(default=0)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='rating_user',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(
                    verbose_name=b'related user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='tribe',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='map',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='gametype',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='game',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(
                    default=0, verbose_name=b'one hour of availability')),
                ('game_type', models.ForeignKey(to='gametype')),
                ('game_map', models.ForeignKey(to='map')),
                ('win_team',  models.IntegerField()),
                ('game_status',  models.IntegerField()),
                ('game_breaks', models.IntegerField()),
                ('submitter', models.ForeignKey(to='rating_user')),
                ('counted_in_score', models.BooleanField(default=False))
            ],
        ),
        migrations.CreateModel(
            name='participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(to='rating_user')),
                ('game', models.ForeignKey(to='game')),
                ('team', models.IntegerField()),
                ('tribe', models.ForeignKey(to='tribe')),
            ],
        ),
        migrations.CreateModel(
            name='player_rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(to='rating_user')),
                ('rating_type', models.IntegerField()),
                ('decimal1', models.DecimalField(max_digits=15, decimal_places=10)),
                ('decimal2', models.DecimalField(max_digits=15, decimal_places=10)),
                ('decimal3', models.DecimalField(max_digits=15, decimal_places=10)),
                ('season', models.ForeignKey(to='season')),
            ],
        ),
    ]
