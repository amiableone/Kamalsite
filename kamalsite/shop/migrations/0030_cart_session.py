# Generated by Django 5.0.1 on 2024-06-22 12:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sessions', '0001_initial'),
        ('shop', '0029_alter_cart_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='session',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sessions.session'),
        ),
    ]
