# Generated by Django 5.0.1 on 2024-03-19 16:04

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_collection_discount_remove_addition_quantity_added_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='colour',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.PositiveBigIntegerField(default=None, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='purchase',
            name='cancelled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='category',
            name='parent_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subcategories', to='shop.category'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='date_created',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='discount',
            name='start',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='like',
            name='liked',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='like',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.product'),
        ),
        migrations.AlterField(
            model_name='product',
            name='collection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.collection'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='payment_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='shipment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.shipment'),
        ),
        migrations.CreateModel(
            name='Defect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100)),
                ('date', models.DateField(auto_now_add=True)),
                ('quantity', models.DecimalField(decimal_places=12, max_digits=12)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.product')),
            ],
        ),
    ]