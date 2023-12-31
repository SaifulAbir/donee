# Generated by Django 3.2.7 on 2021-11-02 10:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0030_user_total_donated_amount'),
        ('goal', '0024_goalsave'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='profile_goal', to='user.profile'),
        ),
    ]
