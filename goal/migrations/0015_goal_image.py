# Generated by Django 3.2.7 on 2021-10-05 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goal', '0014_auto_20211005_0551'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='image',
            field=models.ImageField(default='', upload_to='images/goal_images'),
            preserve_default=False,
        ),
    ]