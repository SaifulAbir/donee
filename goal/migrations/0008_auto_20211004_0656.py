# Generated by Django 3.2.7 on 2021-10-04 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goal', '0007_auto_20211004_0649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='video_type',
            field=models.CharField(blank=True, choices=[('UPDATE', 'Update'), ('THANK_YOU', 'Thank you')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='sdgs',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
