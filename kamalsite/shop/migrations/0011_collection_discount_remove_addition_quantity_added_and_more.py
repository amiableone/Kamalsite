# Generated by Django 5.0.1 on 2024-03-18 09:33

import django.db.models.deletion
import django.utils.timezone
import shop.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_addition_cart_remove_comment_product_like_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=150)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('visible', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=50)),
                ('percent', models.PositiveSmallIntegerField()),
                ('seasonal', models.BooleanField(default=False)),
                ('start', models.DateField(default=django.utils.timezone.now)),
                ('end', models.DateField(default=shop.models.discount_end_date)),
                ('group', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='addition',
            name='quantity_added',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_date',
        ),
        migrations.RemoveField(
            model_name='orderdetail',
            name='quantity_ordered',
        ),
        migrations.AddField(
            model_name='addition',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='last_updated',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='addition',
            name='date_added',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='order',
            name='date_created',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='min_order_quantity',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=75),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=12),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='available quantity'),
        ),
        migrations.AlterField(
            model_name='product',
            name='unit_measure',
            field=models.CharField(default='units', max_length=30),
        ),
        migrations.AddField(
            model_name='product',
            name='collection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.collection'),
        ),
        migrations.AddField(
            model_name='collection',
            name='discount',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.discount'),
        ),
        migrations.AddField(
            model_name='product',
            name='discount',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.discount'),
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shipment_address', models.CharField(max_length=300)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='shop.order')),
                ('payment_date', models.DateTimeField(auto_now=True)),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.shipment')),
            ],
        ),
    ]
