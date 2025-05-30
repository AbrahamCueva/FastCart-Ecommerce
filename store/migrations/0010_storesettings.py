# Generated by Django 4.2 on 2025-03-30 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_slider_button_link_slider_button_text_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_name', models.CharField(max_length=255, verbose_name='Nombre de la Tienda')),
                ('logo', models.ImageField(upload_to='settings/', verbose_name='Logo de la Tienda')),
                ('favicon', models.ImageField(upload_to='settings/', verbose_name='Favicon (Ícono de pestaña)')),
                ('address', models.TextField(verbose_name='Dirección')),
                ('phone', models.CharField(max_length=20, verbose_name='Teléfono')),
                ('email', models.EmailField(max_length=254, verbose_name='Correo Electrónico')),
                ('facebook', models.URLField(blank=True, null=True, verbose_name='Facebook')),
                ('instagram', models.URLField(blank=True, null=True, verbose_name='Instagram')),
                ('twitter', models.URLField(blank=True, null=True, verbose_name='Twitter')),
                ('youtube', models.URLField(blank=True, null=True, verbose_name='YouTube')),
                ('linkedin', models.URLField(blank=True, null=True, verbose_name='LinkedIn')),
                ('seo_title', models.CharField(max_length=255, verbose_name='Título SEO')),
                ('seo_description', models.TextField(verbose_name='Descripción SEO')),
                ('seo_keywords', models.CharField(max_length=500, verbose_name='Palabras Clave SEO')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Última Actualización')),
            ],
            options={
                'verbose_name': 'Configuración de la Tienda',
                'verbose_name_plural': 'Configuraciones de la Tienda',
            },
        ),
    ]
