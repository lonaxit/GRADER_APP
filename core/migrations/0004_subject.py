# Generated by Django 4.1.6 on 2023-06-26 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_schoolclass'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('subject_code', models.CharField(max_length=100)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
