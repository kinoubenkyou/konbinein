# Generated by Django 4.1.4 on 2023-03-30 05:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0011_user_password_resetting_token"),
    ]

    operations = [
        migrations.RenameField(
            model_name="orderitem",
            old_name="unit_price",
            new_name="price",
        ),
    ]
