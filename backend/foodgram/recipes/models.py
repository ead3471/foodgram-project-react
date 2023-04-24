from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=20,
                            unique=True)
    color = models.CharField(default='#FFFFFF',
                             max_length=7,
                             unique=True,
                             validators=(RegexValidator(regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"),))
    slug = models.SlugField()

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Ingredient name')
    measurement_unit = models.CharField(max_length=20,
                                        verbose_name='Ingredient measure unit')

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipies')
    name = models.CharField(max_length=200,
                            verbose_name='Recipe name')
    image = models.ImageField(upload_to='recipies/', verbose_name='Food photo')
    text = models.TextField()
    cooking_time = models.IntegerField(validators=(MinValueValidator(1),),
                                       verbose_name='Coocking time, minutes')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ingredients',
                                         null=True
                                         # related_name='recipies'
                                         )
    tag = models.ManyToManyField(Tag,
                                 verbose_name='Tags',
                                 related_name='recipies')

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipies'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ingredient',
                                   related_name='recipe_ingredients')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Recipe',
                               related_name='recipe_ingredients'
                               )
    amount = models.PositiveIntegerField(
        verbose_name='Ingredient amount', default=1)

    def __str__(self) -> str:
        return self.ingredient.name

    class Meta:
        unique_together = ['ingredient', 'recipe']
        verbose_name = 'Recipe Ingredient'


class Favorites(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='User',
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe,
                               related_name='in_favorites',
                               on_delete=models.CASCADE,
                               verbose_name='Recipe')

    def __str__(self) -> str:
        return f'{self.user.username}_{self.recipe}'

    class Meta:
        ordering = ['user_id']
        unique_together = ['user', 'recipe']
        verbose_name_plural = 'Favorites'


class ShopingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='User',
                             related_name='shopping_carts')

    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Recipies',
                               related_name='shopping_carts')

    class Meta:
        ordering = ['user']
        verbose_name = 'Shopping list'
        verbose_name_plural = 'Shopping lists'
