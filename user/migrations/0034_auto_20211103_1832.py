# Generated by Django 3.2.7 on 2021-11-03 12:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0033_profile_total_follow_count'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='profilefollow',
            table='profilefollow',
        ),
        migrations.AlterModelTable(
            name='userfollow',
            table='userfollow',
        ),
    ]
