# Generated by Django 5.0.1 on 2024-04-17 17:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0021_rename_ready_to_order_addition_order_now'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchase',
            old_name='payment_date',
            new_name='date_created',
        ),
    ]