# Generated by Django 5.1.4 on 2025-03-10 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0019_alter_review_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='content',
            field=models.TextField(verbose_name='Отзыв'),
        ),
    ]
