# Generated by Django 5.1.4 on 2025-03-17 17:26

import django_ckeditor_5.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_alter_order_postal_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='my_comment',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, null=True, verbose_name='Комментарий, скрытый от покупателя'),
        ),
    ]
