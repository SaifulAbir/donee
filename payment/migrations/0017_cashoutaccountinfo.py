# Generated by Django 3.2.7 on 2021-11-24 07:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0048_alter_ngouser_user'),
        ('payment', '0016_auto_20211123_1155'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashoutAccountInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_by', models.CharField(max_length=255, null=True)),
                ('modified_at', models.DateTimeField(null=True)),
                ('name', models.CharField(max_length=150)),
                ('type', models.CharField(max_length=130)),
                ('account_number', models.CharField(max_length=130)),
                ('profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='profile_cashout_account_info', to='user.profile')),
            ],
            options={
                'verbose_name': 'CashoutAccountInfo',
                'verbose_name_plural': 'CashoutAccountInfo',
                'db_table': 'CashoutAccountInfo',
            },
        ),
    ]
