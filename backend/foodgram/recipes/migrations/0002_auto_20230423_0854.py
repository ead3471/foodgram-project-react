# Generated by Django 3.2.18 on 2023-04-23 08:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'verbose_name': 'Recipe Ingredient'},
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(default='#FFFFFF', max_length=7, unique=True, validators=[django.core.validators.RegexValidator(regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')]),
        ),
    ]