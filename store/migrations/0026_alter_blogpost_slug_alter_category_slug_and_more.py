# Generated by Django 4.2 on 2025-04-04 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0025_remove_storesettings_mercadopago_access_token_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='slug',
            field=models.SlugField(blank=True, max_length=500, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='categorypost',
            name='slug',
            field=models.SlugField(max_length=500, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=500, unique=True),
        ),
    ]
