# Generated by Django 4.1.4 on 2023-04-07 05:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "main",
            "0013_remove_staff_main_organizationuser_organization_id_user_id_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="organization",
            name="code",
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]
