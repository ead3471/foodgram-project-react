from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from colorfield.fields import ColorField

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=20,
                            unique=True)
    color = models.CharField(default='#FFFFFF',
                             max_length=7,
                             unique=True)
    slug = models.SlugField()

    def __str__(self) -> str:
        return self.name


class Ingridient(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Ingridient name')
    measure_unit = models.CharField(max_length=20,
                                    verbose_name='Ingridient measure unit')

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipies')
    name = models.CharField(max_length=200,
                            verbose_name='Recipe name')
    image = models.ImageField(upload_to='recipies/', verbose_name='Food photo')
    description = models.TextField()
    coocking_time = models.IntegerField(validators=(MinValueValidator(1),))
    ingridients = models.ManyToManyField(Ingridient,
                                         through='RecipeIngridient',
                                         verbose_name='Ingridients',
                                         related_name='recipies')
    tags = models.ManyToManyField(Tag,
                                  verbose_name='Tags',
                                  related_name='recipies')

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipies'


class RecipeIngridient(models.Model):
    ingridient = models.ForeignKey(Ingridient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ingridient',
                                   related_name='recipe_ingridients')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Recipe',
                               related_name='ingridiens',
                               )
    amount = models.PositiveIntegerField(verbose_name='Ingridient amount')


class Favorites(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='User')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Recipe')

    def __str__(self) -> str:
        return f'{self.user.username}_{self.recipe}'

    class Meta:
        ordering = ['user_id']
        unique_together = ['user', 'recipe']


class ShopingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='User',
                             related_name='purchases')

    recipies = models.ManyToManyField(Recipe,
                                      verbose_name='Recipies',
                                      related_name='shopping_cards')

    class Meta:
        ordering = ['user']
        verbose_name = 'Shopping list'
        verbose_name_plural = 'Shopping lists'
