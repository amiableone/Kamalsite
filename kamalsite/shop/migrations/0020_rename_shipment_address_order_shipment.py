# Generated by Django 5.0.1 on 2024-04-16 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0019_alter_order_purchaser_email_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='shipment_address',
            new_name='shipment',
        ),
    ]