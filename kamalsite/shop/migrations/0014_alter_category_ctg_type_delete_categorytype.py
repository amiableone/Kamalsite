# Generated by Django 5.0.1 on 2024-04-09 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0013_categorytype_rename_paid_order_confirmed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='ctg_type',
            field=models.CharField(help_text='e.g. size, colour, furniture type, etc.', max_length=50),
        ),
        migrations.DeleteModel(
            name='CategoryType',
        ),
    ]
