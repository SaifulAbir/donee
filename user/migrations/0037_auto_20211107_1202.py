# Generated by Django 3.2.7 on 2021-11-07 06:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0036_user_total_following_count'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profilefollow',
            options={'verbose_name': 'ProfileFollow', 'verbose_name_plural': 'Follows'},
        ),
        migrations.AlterModelOptions(
            name='userfollow',
            options={'verbose_name': 'UserFollow', 'verbose_name_plural': 'Follows'},
        ),
    ]
