# Generated by Django 3.2.9 on 2021-11-30 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0048_alter_ngouser_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='verification_id',
            field=models.CharField(default='null', max_length=40),
        ),
    ]
