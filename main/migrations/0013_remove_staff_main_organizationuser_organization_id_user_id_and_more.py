# Generated by Django 4.1.4 on 2023-03-30 07:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0012_rename_unit_price_orderitem_price"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="staff",
            name="main_organizationuser_organization_id_user_id",
        ),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.UniqueConstraint(
                models.F("code"),
                models.F("organization"),
                name="main_order_code_organization_id",
            ),
        ),
        migrations.AddConstraint(
            model_name="staff",
            constraint=models.UniqueConstraint(
                models.F("organization"),
                models.F("user"),
                name="main_staff_organization_id_user_id",
            ),
        ),
    ]
