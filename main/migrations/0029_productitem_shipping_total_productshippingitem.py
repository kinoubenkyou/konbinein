# Generated by Django 4.1.4 on 2023-08-06 04:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0028_alter_productitem_item_total_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="productitem",
            name="shipping_total",
            field=models.DecimalField(decimal_places=4, max_digits=19, null=True),
        ),
        migrations.CreateModel(
            name="ProductShippingItem",
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
                ("subtotal", models.DecimalField(decimal_places=4, max_digits=19)),
                ("total", models.DecimalField(decimal_places=4, max_digits=19)),
                ("unit_fee", models.DecimalField(decimal_places=4, max_digits=19)),
                (
                    "product_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="main.productitem",
                    ),
                ),
                (
                    "product_shipping",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="main.productshipping",
                    ),
                ),
            ],
        ),
    ]