# Generated by Django 3.2.7 on 2021-10-24 04:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0027_alter_profile_user'),
        ('payment', '0009_walletdistribution'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='profile_wallet', to='user.profile'),
        ),
    ]
