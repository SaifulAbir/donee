# Generated by Django 3.2.7 on 2021-10-07 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0024_profilesdgs'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='invitation_id',
            field=models.CharField(default='null', max_length=40),
        ),
    ]
