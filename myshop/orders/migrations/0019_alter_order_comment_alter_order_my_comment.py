# Generated by Django 5.1.4 on 2025-03-26 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0018_alter_orderitem_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='order',
            name='my_comment',
            field=models.TextField(blank=True, null=True, verbose_name='Комментарий, скрытый от покупателя'),
        ),
    ]
