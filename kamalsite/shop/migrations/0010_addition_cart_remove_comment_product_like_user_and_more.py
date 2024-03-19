# Generated by Django 5.0.1 on 2024-03-12 15:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myauth', '0002_alter_user_options_alter_user_table'),
        ('shop', '0009_remove_user_before_replacing_it_with_django_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
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
    ]