# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-11-19 18:55


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wlmaps', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='map',
            name='rating_score',
        ),
        migrations.RemoveField(
            model_name='map',
            name='rating_votes',
        ),
        migrations.AlterField(
            model_name='map',
            name='hint',
            field=models.TextField(blank=True, verbose_name=b'Hint'),
        ),
        migrations.AlterField(
            model_name='map',
            name='world_name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]