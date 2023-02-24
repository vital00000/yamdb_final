# Generated by Django 2.2.16 on 2022-11-20 04:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_auto_20221119_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.PositiveSmallIntegerField(db_index=True, validators=[django.core.validators.MaxValueValidator(2022)], verbose_name='Дата релиза'),
        ),
    ]
