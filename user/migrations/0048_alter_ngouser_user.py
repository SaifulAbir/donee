# Generated by Django 3.2.7 on 2021-11-17 11:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0047_alter_ngouser_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ngouser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_ngo_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
