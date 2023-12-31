# Generated by Django 3.2.9 on 2021-12-09 05:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0050_country_country_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificationIncorporation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_by', models.CharField(max_length=255, null=True)),
                ('modified_at', models.DateTimeField(null=True)),
                ('file', models.FileField(upload_to='certification_of_incorporation')),
                ('profile', models.ForeignKey(db_column='profile', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='profile_certification', to='user.profile')),
            ],
            options={
                'verbose_name': 'Certification of incorporation',
                'verbose_name_plural': 'Certification of incorporation',
                'db_table': 'Certification_of_incorporation',
            },
        ),
    ]
