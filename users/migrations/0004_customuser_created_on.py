# Generated by Django 4.1.6 on 2025-03-19 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_customuser_date_joined'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='created_on',
            field=models.DateField(default='2023-02-02'),
        ),
    ]
