# Generated by Django 5.1.4 on 2025-03-06 18:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='postal_code',
            field=models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(message='Индекс должен состоять только из цифр.', regex='^\\d+$')], verbose_name='Почтовый индекс'),
        ),
    ]
