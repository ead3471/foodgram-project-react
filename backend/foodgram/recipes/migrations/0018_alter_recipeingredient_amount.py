# Generated by Django 3.2.18 on 2023-05-01 11:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0017_auto_20230427_0857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Ingredient amount'),
        ),
    ]