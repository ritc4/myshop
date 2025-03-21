# Generated by Django 5.1.4 on 2025-03-15 21:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0013_alter_discount_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='phone',
            field=models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='Телефон должен быть в формате: +7 (XXX) XXX-XX-XX, где X - цифры.', regex='^\\+7 \\(\\d{3}\\) \\d{3}-\\d{2}-\\d{2}$')], verbose_name='Телефон'),
        ),
    ]
