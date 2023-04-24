# Generated by Django 3.2.18 on 2023-04-24 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20230423_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(null=True, through='recipes.RecipeIngredient', to='recipes.Ingredient', verbose_name='Ingredients'),
        ),
    ]