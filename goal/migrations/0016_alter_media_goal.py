# Generated by Django 3.2.7 on 2021-10-05 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goal', '0015_goal_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='goal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='goal_media', to='goal.goal'),
        ),
    ]
