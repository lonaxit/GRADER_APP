# Generated by Django 4.1.6 on 2025-03-19 19:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_remove_customuser_created_on'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='date_joined',
        ),
    ]
