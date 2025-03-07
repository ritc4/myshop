# Generated by Django 5.1.4 on 2025-03-06 00:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='phone',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Телефон должен начинаться с +7 и содержать 10-12 цифр.', regex='^\\+7\\d{10,12}$')], verbose_name='Телефон'),
        ),
    ]
