# Generated by Django 5.1.4 on 2025-03-02 23:45

import django_ckeditor_5.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, null=True, verbose_name='Комментарий'),
        ),
    ]
