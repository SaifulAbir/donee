# Generated by Django 3.2.7 on 2021-09-21 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20210921_0745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='ngo_profile_id',
            field=models.CharField(blank=True, default='null', max_length=100, null=True),
        ),
    ]
