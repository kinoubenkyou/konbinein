# Generated by Django 4.1.4 on 2023-05-07 09:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0021_order_total_productitem_total"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="total",
            field=models.DecimalField(decimal_places=4, max_digits=19),
        ),
        migrations.AlterField(
            model_name="productitem",
            name="total",
            field=models.DecimalField(decimal_places=4, max_digits=19),
        ),
    ]
