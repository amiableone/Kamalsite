# Generated by Django 5.0.1 on 2024-03-07 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_user_product_constraint_to_like_and_changes_to_other_models'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='currency',
        ),
    ]
