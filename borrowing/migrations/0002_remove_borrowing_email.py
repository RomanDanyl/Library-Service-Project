# Generated by Django 5.1.1 on 2024-10-02 15:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("borrowing", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="borrowing",
            name="email",
        ),
    ]
