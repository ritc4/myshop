# Generated by Django 5.1.4 on 2025-02-18 02:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_alter_order_delivery_method_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deliverymethod',
            options={'ordering': ['-title']},
        ),
    ]
