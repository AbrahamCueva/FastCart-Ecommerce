# Generated by Django 4.2 on 2025-03-24 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='country',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
