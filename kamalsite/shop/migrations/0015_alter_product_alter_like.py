# Generated by Django 5.0.1 on 2024-04-09 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_alter_category_ctg_type_delete_categorytype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='colour',
        ),
        migrations.AlterField(
            model_name='like',
            name='liked',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='min_order_quantity',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=12),
            preserve_default=False,
        ),
    ]