# Generated by Django 5.1.4 on 2025-03-08 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_alter_review_kachestvo_rating_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='kachestvo_rating',
            field=models.PositiveIntegerField(max_length=1),
        ),
        migrations.AlterField(
            model_name='review',
            name='obsluga_rating',
            field=models.PositiveIntegerField(max_length=1),
        ),
        migrations.AlterField(
            model_name='review',
            name='sroki_rating',
            field=models.PositiveIntegerField(max_length=1),
        ),
    ]
