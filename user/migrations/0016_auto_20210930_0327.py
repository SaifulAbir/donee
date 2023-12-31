# Generated by Django 3.2.7 on 2021-09-30 03:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0015_auto_20210929_1225'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='location',
        ),
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.ForeignKey(blank=True, db_column='country', null=True, on_delete=django.db.models.deletion.PROTECT, to='user.country'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='country',
            field=models.ForeignKey(blank=True, db_column='country', null=True, on_delete=django.db.models.deletion.PROTECT, to='user.country'),
        ),
    ]
