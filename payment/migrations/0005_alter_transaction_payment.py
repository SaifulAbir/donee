# Generated by Django 3.2.7 on 2021-10-18 07:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_auto_20211018_0740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='payment',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='payment_transaction', to='payment.payment', verbose_name='payment'),
        ),
    ]
