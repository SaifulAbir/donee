# Generated by Django 3.2.7 on 2021-10-04 08:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0023_auto_20211004_0502'),
        ('goal', '0009_alter_sdgs_thumbnail'),
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_by', models.CharField(max_length=255, null=True)),
                ('modified_at', models.DateTimeField(null=True)),
                ('type', models.CharField(choices=[('PGW', 'PGW'), ('NGO', 'NGO'), ('PLATFORM', 'Platform')], max_length=50)),
                ('value', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Setting',
                'verbose_name_plural': 'Settings',
                'db_table': 'settings',
            },
        ),
        migrations.RemoveField(
            model_name='goal',
            name='profile_id',
        ),
        migrations.AddField(
            model_name='goal',
            name='profile',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, to='user.profile'),
            preserve_default=False,
        ),
    ]