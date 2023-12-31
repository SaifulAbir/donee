# Generated by Django 3.2.7 on 2021-10-27 11:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goal', '0022_alter_goal_paid_amount'),
        ('payment', '0010_alter_wallet_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='goal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='goal_payment', to='goal.goal'),
        ),
    ]
