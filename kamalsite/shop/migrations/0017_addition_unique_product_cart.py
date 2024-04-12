# Generated by Django 5.0.1 on 2024-04-12 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_alter_product_and_addition_delete_defect'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='addition',
            constraint=models.UniqueConstraint(fields=('product', 'cart'), name='unique_product_cart'),
        ),
    ]