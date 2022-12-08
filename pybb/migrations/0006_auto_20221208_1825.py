# Generated by Django 2.2.28 on 2022-12-08 18:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pybb', '0005_auto_20181221_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='hash',
            field=models.CharField(blank=True, db_index=True, default='', max_length=40, verbose_name='Hash'),
        ),
        migrations.AlterField(
            model_name='forum',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='forum',
            name='moderator_group',
            field=models.ForeignKey(blank=True, default=None, help_text='Users in this Group will have administrative permissions in this Forum.', null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='post',
            name='hidden',
            field=models.BooleanField(blank=True, default=False, verbose_name='Hidden'),
        ),
        migrations.AlterField(
            model_name='post',
            name='markup',
            field=models.CharField(choices=[('markdown', 'markdown'), ('bbcode', 'bbcode')], default='markdown', max_length=15, verbose_name='Markup'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='closed',
            field=models.BooleanField(blank=True, default=False, verbose_name='Closed'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='sticky',
            field=models.BooleanField(blank=True, default=False, verbose_name='Sticky'),
        ),
    ]
