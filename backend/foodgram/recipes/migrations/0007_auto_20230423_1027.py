# Generated by Django 3.2.18 on 2023-04-23 10:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_recipeingredient_ingredient'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='measure_unit',
            new_name='measurement_unit',
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.recipe', verbose_name='Recipe'),
        ),
    ]
