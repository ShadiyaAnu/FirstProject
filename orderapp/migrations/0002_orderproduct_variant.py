# Generated by Django 5.0 on 2024-01-31 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orderapp', '0001_initial'),
        ('userapp', '0008_alter_product_product_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproduct',
            name='variant',
            field=models.ManyToManyField(blank=True, to='userapp.variant'),
        ),
    ]