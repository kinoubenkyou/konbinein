# Generated by Django 4.1.4 on 2023-04-09 10:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0015_alter_organization_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
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
                ("code", models.CharField(max_length=255, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("price", models.DecimalField(decimal_places=4, max_digits=19)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="main.organization",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.UniqueConstraint(
                models.F("code"),
                models.F("organization"),
                name="main_product_code_organization_id",
            ),
        ),
    ]