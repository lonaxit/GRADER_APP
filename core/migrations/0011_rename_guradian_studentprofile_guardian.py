# Generated by Django 4.1.6 on 2023-06-28 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_studentprofile_date_created_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='studentprofile',
            old_name='guradian',
            new_name='guardian',
        ),
    ]
