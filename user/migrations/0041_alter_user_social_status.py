# Generated by Django 3.2.7 on 2021-11-11 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0040_user_social_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='social_status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]