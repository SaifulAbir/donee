# Generated by Django 3.2.7 on 2021-11-07 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0035_auto_20211103_1857'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='total_following_count',
            field=models.IntegerField(default=0),
        ),
    ]