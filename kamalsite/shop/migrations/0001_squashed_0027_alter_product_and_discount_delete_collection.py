# Generated by Django 5.0.1 on 2024-05-11 18:30

import datetime
import django.db.models.deletion
import django.utils.timezone
import shop.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('shop', '0001_initial'), ('shop', '0002_product_additions_product_likes'), ('shop', '0003_product_purchases'), ('shop', '0004_user_remove_product_additions_remove_product_likes_and_more'), ('shop', '0005_remove_user_user_type_sitevisit_productvisit'), ('shop', '0006_user_product_constraint_to_like_and_changes_to_other_models'), ('shop', '0007_remove_product_currency'), ('shop', '0008_remove_redundant_fields_in_product'), ('shop', '0009_remove_user_before_replacing_it_with_django_user'), ('shop', '0010_addition_cart_remove_comment_product_like_user_and_more'), ('shop', '0011_collection_discount_remove_addition_quantity_added_and_more'), ('shop', '0012_product_colour_product_sku_purchase_cancelled_and_more'), ('shop', '0013_categorytype_rename_paid_order_confirmed_and_more'), ('shop', '0014_alter_category_ctg_type_delete_categorytype'), ('shop', '0015_alter_product_alter_like'), ('shop', '0016_alter_product_and_addition_delete_defect'), ('shop', '0017_addition_unique_product_cart'), ('shop', '0018_order_as_individual_order_purchaser_and_more'), ('shop', '0019_alter_order_purchaser_email_and_more'), ('shop', '0020_rename_shipment_address_order_shipment'), ('shop', '0021_rename_ready_to_order_addition_order_now'), ('shop', '0022_rename_payment_date_purchase_date_created'), ('shop', '0023_alter_shipment_fields'), ('shop', '0024_shipment_zip_shipment_unique_user_address'), ('shop', '0025_alter_like_product_rel_name'), ('shop', '0026_alter_model_category'), ('shop', '0027_alter_product_and_discount_delete_collection')]

    initial = True

    dependencies = [
        ('myauth', '0002_alter_user_options_alter_user_table'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signed_up', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=20, null=True)),
                ('user_email', models.EmailField(max_length=254, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField()),
                ('currency', models.CharField(choices=[('RUB', 'Rub'), ('USD', 'Usd')], default='RUB', max_length=4)),
                ('in_stock', models.BooleanField(default=False)),
                ('min_order_amount', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('min_order_quantity', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=2, null=True)),
                ('quantity', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='available quantity')),
                ('unit_measure', models.CharField(default='units', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Addition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateField()),
                ('quantity_added', models.DecimalField(decimal_places=2, max_digits=5)),
                ('ready_to_order', models.BooleanField(default=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry', models.TextField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.user')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.user')),
            ],
        ),
        migrations.CreateModel(
            name='OrderDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_ordered', models.DecimalField(decimal_places=2, max_digits=5)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(through='shop.OrderDetail', to='shop.product'),
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='shop.user')),
                ('products', models.ManyToManyField(through='shop.Addition', to='shop.product')),
            ],
        ),
        migrations.AddField(
            model_name='addition',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.cart'),
        ),
        migrations.CreateModel(
            name='SiteVisit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visit_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ProductVisit',
            fields=[
                ('from_main', models.BooleanField(default=False)),
                ('from_catalog', models.BooleanField(default=False)),
                ('from_similar', models.BooleanField(default=False)),
            ],
            bases=('shop.sitevisit',),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=300)),
                ('products', models.ManyToManyField(to='shop.product')),
                ('parent_category', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='shop.category')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='date_created',
            field=models.DateTimeField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_date',
            field=models.DateTimeField(default=None),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked_by', to='shop.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked_products', to='shop.user')),
                ('liked', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddConstraint(
            model_name='like',
            constraint=models.UniqueConstraint(fields=('user', 'product'), name='unique_user_product'),
        ),
        migrations.DeleteModel(
            name='ProductVisit',
        ),
        migrations.DeleteModel(
            name='SiteVisit',
        ),
        migrations.RemoveField(
            model_name='product',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='product',
            name='in_stock',
        ),
        migrations.RemoveField(
            model_name='product',
            name='min_order_amount',
        ),
        migrations.RemoveField(
            model_name='addition',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='addition',
            name='product',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='products',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='user',
        ),
        migrations.RemoveField(
            model_name='like',
            name='user',
        ),
        migrations.RemoveField(
            model_name='order',
            name='user',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='user',
        ),
        migrations.RemoveConstraint(
            model_name='like',
            name='unique_user_product',
        ),
        migrations.DeleteModel(
            name='Addition',
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.CreateModel(
            name='Addition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateField()),
                ('quantity_added', models.DecimalField(decimal_places=2, max_digits=5)),
                ('ready_to_order', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='comment',
            name='product',
        ),
        migrations.AddField(
            model_name='like',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='liked_products', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='like',
            constraint=models.UniqueConstraint(fields=('user', 'product'), name='unique_user_product'),
        ),
        migrations.AddField(
            model_name='addition',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product'),
        ),
        migrations.AddField(
            model_name='cart',
            name='products',
            field=models.ManyToManyField(through='shop.Addition', to='shop.product'),
        ),
        migrations.AddField(
            model_name='addition',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.cart'),
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
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
                ('start', models.DateField(default=datetime.date.today)),
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
            model_name='orderdetail',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='addition',
            name='date_added',
        ),
        migrations.RemoveField(
            model_name='category',
            name='description',
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='order',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='min_order_quantity',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=12),
            preserve_default=False,
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
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.PositiveBigIntegerField(default=None, unique=True),
            preserve_default=False,
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
            model_name='like',
            name='liked',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='like',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL),
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
        migrations.RenameField(
            model_name='order',
            old_name='paid',
            new_name='confirmed',
        ),
        migrations.AddField(
            model_name='order',
            name='receiver',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='shipment_address',
            field=models.CharField(default=None, max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='shipment_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='order',
            name='shipped',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='shop.order')),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('cancelled', models.BooleanField(default=False)),
                ('payment_received', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='ctg_type',
            field=models.CharField(help_text='e.g. size, colour, furniture type, etc.', max_length=50),
        ),
        migrations.AddField(
            model_name='product',
            name='date_created',
            field=models.DateField(default=datetime.date.today, help_text='when first appeared in the catalog'),
        ),
        migrations.AddField(
            model_name='product',
            name='in_production',
            field=models.BooleanField(default=True),
        ),
        migrations.AddConstraint(
            model_name='addition',
            constraint=models.UniqueConstraint(fields=('product', 'cart'), name='unique_product_cart'),
        ),
        migrations.AddField(
            model_name='order',
            name='as_individual',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='purchaser',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='purchaser_email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AddField(
            model_name='order',
            name='receiver_phone',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='shipment_address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.shipment'),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_details', to='shop.order'),
        ),
        migrations.AddConstraint(
            model_name='orderdetail',
            constraint=models.UniqueConstraint(fields=('product', 'order'), name='unique_product_order'),
        ),
        migrations.RenameField(
            model_name='order',
            old_name='shipment_address',
            new_name='shipment',
        ),
        migrations.RenameField(
            model_name='addition',
            old_name='ready_to_order',
            new_name='order_now',
        ),
        migrations.RenameField(
            model_name='purchase',
            old_name='payment_date',
            new_name='date_created',
        ),
        migrations.RenameField(
            model_name='shipment',
            old_name='shipment_address',
            new_name='address',
        ),
        migrations.AlterField(
            model_name='shipment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shipment',
            name='zip',
            field=models.CharField(default=0, max_length=10),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='shipment',
            constraint=models.UniqueConstraint(fields=('user', 'address'), name='unique_user_address'),
        ),
        migrations.AlterField(
            model_name='like',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='shop.product'),
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name', 'value']},
        ),
        migrations.RenameField(
            model_name='category',
            old_name='parent_category',
            new_name='parent',
        ),
        migrations.RenameField(
            model_name='category',
            old_name='name',
            new_name='value',
        ),
        migrations.RenameField(
            model_name='category',
            old_name='ctg_type',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='product',
            name='collection',
        ),
        migrations.RemoveField(
            model_name='product',
            name='sku',
        ),
        migrations.AddField(
            model_name='discount',
            name='category',
            field=models.ManyToManyField(to='shop.category'),
        ),
        migrations.DeleteModel(
            name='Collection',
        ),
    ]
