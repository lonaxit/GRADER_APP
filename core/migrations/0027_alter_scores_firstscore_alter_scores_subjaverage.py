# Generated by Django 4.1.6 on 2023-07-22 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_alter_scores_firstscore'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scores',
            name='firstscore',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='scores',
            name='subjaverage',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
