# Generated by Django 3.2.7 on 2021-11-14 07:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0044_alter_ngouserrole_role_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ngouser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='role_user', to=settings.AUTH_USER_MODEL, unique=True),
        ),
    ]
