# Generated by Django 3.2.7 on 2021-10-04 06:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goal', '0005_auto_20211004_0611'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='goalsdgs',
            options={'verbose_name': 'GoalSDGS', 'verbose_name_plural': 'GoalSDGS'},
        ),
        migrations.AlterField(
            model_name='goalsdgs',
            name='goal',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='goal_sdgs', to='goal.goal', verbose_name='Goal'),
            preserve_default=False,
        ),
        migrations.AlterModelTable(
            name='goalsdgs',
            table='goal_sdgs',
        ),
    ]
