# Generated by Django 4.1.4 on 2023-01-11 08:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0002_organization_order_organization"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("email", models.EmailField(max_length=254, unique=True)),
                ("name", models.CharField(max_length=255, null=True)),
                ("hashed_password", models.CharField(max_length=255)),
            ],
        ),
    ]
