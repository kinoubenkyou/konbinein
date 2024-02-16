# Generated by Django 4.2.8 on 2024-02-15 14:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0036_alter_order_product_shipping_total"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="order_shipping_total",
            field=models.DecimalField(decimal_places=4, default=0, max_digits=19),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="OrderShippingItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fixed_fee", models.DecimalField(decimal_places=4, max_digits=19)),
                ("item_total", models.DecimalField(decimal_places=4, max_digits=19)),
                ("name", models.CharField(max_length=255)),
                ("unit_fee", models.DecimalField(decimal_places=4, max_digits=19)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.order"
                    ),
                ),
                (
                    "order_shipping",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="main.ordershipping",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
