# Generated by Django 4.1.4 on 2023-05-07 08:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0019_productshipping_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="code",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="product",
            name="code",
            field=models.CharField(max_length=255),
        ),
    ]
