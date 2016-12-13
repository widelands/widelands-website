# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('displayname', models.CharField(max_length=100)),
                ('image_url', models.CharField(max_length=256)),
                ('graph_url', models.CharField(max_length=256)),
                ('imagemap', models.TextField()),
                ('size', models.CharField(max_length=1, choices=[(b'S', b'small'), (b'M', b'medium'), (
                    b'B', b'big'), (b'I', b'mine'), (b'P', b'port'), (b'H', b'headquarters')])),
                ('type', models.CharField(max_length=1, choices=[(b'P', b'productionsite'), (
                    b'W', b'warehouse'), (b'M', b'militarysite'), (b'T', b'trainingsite')])),
                ('help', models.TextField(blank=True)),
                ('build_costs', models.CharField(max_length=100, blank=True)),
                ('workers_count', models.CharField(max_length=100, blank=True)),
                ('store_count', models.CharField(max_length=100, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tribe',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('displayname', models.CharField(max_length=100)),
                ('descr', models.TextField()),
                ('icon_url', models.CharField(max_length=256)),
                ('network_pdf_url', models.CharField(max_length=256)),
                ('network_gif_url', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Ware',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('displayname', models.CharField(max_length=100)),
                ('image_url', models.CharField(max_length=256)),
                ('graph_url', models.CharField(max_length=256)),
                ('imagemap', models.TextField()),
                ('help', models.TextField(max_length=256)),
                ('tribe', models.ForeignKey(to='wlhelp.Tribe')),
            ],
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('displayname', models.CharField(max_length=100)),
                ('image_url', models.CharField(max_length=256)),
                ('graph_url', models.CharField(max_length=256)),
                ('imagemap', models.TextField()),
                ('help', models.TextField(max_length=256)),
                ('exp', models.TextField(max_length=8)),
                ('becomes', models.OneToOneField(
                    related_name='trained_by_experience', null=True, blank=True, to='wlhelp.Worker')),
                ('tribe', models.ForeignKey(to='wlhelp.Tribe')),
            ],
        ),
        migrations.AddField(
            model_name='building',
            name='build_wares',
            field=models.ManyToManyField(
                related_name='build_ware_for_buildings', to='wlhelp.Ware', blank=True),
        ),
        migrations.AddField(
            model_name='building',
            name='enhancement',
            field=models.OneToOneField(
                related_name='enhanced_from', null=True, blank=True, to='wlhelp.Building'),
        ),
        migrations.AddField(
            model_name='building',
            name='output_wares',
            field=models.ManyToManyField(
                related_name='produced_by_buildings', to='wlhelp.Ware', blank=True),
        ),
        migrations.AddField(
            model_name='building',
            name='output_workers',
            field=models.ManyToManyField(
                related_name='trained_by_buildings', to='wlhelp.Worker', blank=True),
        ),
        migrations.AddField(
            model_name='building',
            name='store_wares',
            field=models.ManyToManyField(
                related_name='stored_ware_for_buildings', to='wlhelp.Ware', blank=True),
        ),
        migrations.AddField(
            model_name='building',
            name='tribe',
            field=models.ForeignKey(to='wlhelp.Tribe'),
        ),
        migrations.AddField(
            model_name='building',
            name='workers_types',
            field=models.ManyToManyField(
                related_name='workers_for_buildings', to='wlhelp.Worker', blank=True),
        ),
    ]
