# Generated by Django 3.2.7 on 2021-11-23 08:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goal', '0029_alter_goal_status'),
        ('payment', '0014_auto_20211118_0831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashout',
            name='goal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='goal_cashout', to='goal.goal'),
        ),
    ]
