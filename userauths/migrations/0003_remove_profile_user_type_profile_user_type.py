# Generated by Django 4.2 on 2025-03-28 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0002_alter_profile_user_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='user_Type',
        ),
        migrations.AddField(
            model_name='profile',
            name='user_type',
            field=models.CharField(blank=True, choices=[('Vendor', 'Proveedor'), ('Customer', 'Cliente')], default=None, max_length=255, null=True),
        ),
    ]
