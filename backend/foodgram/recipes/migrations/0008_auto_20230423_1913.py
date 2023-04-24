# Generated by Django 3.2.18 on 2023-04-23 19:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0007_auto_20230423_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopingcart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_carts', to='recipes.recipe', verbose_name='Recipies'),
        ),
        migrations.AlterField(
            model_name='shopingcart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_carts', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
