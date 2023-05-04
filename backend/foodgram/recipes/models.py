from django.contrib.auth import get_user_model
from django.core.validators import (MinLengthValidator, MinValueValidator,
                                    RegexValidator)
from django.db.models import (CASCADE, CharField, DateTimeField, FloatField,
                              ForeignKey, ImageField, IntegerField,
                              ManyToManyField, Model, TextField, SlugField)

from recipes import Setup

from .validators import BorderedMinValueValidator


User = get_user_model()


class Tag(Model):
    name = CharField(max_length=20,
                     unique=True)

    color = CharField(default='#FFFFFF',
                      max_length=7,
                      unique=True,
                      validators=(
                          RegexValidator(
                              regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"),)
                      )

    slug = SlugField()

    def __str__(self) -> str:
        return self.name


class Ingredient(Model):
    name = CharField(max_length=Setup.MAX_INGREDIENT_NAME_LENGTH,
                     verbose_name='Ingredient name')

    measurement_unit = CharField(max_length=Setup.MAX_MEASUREMENT_UNIT_LENGTH,
                                 verbose_name='Ingredient measure unit')

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Recipe(Model):

    author = ForeignKey(User,
                        on_delete=CASCADE,
                        related_name='recipes')

    name = CharField(max_length=Setup.MAX_RECIPE_NAME_LENGTH,
                     verbose_name='Recipe name',
                     validators=(
                         MinLengthValidator(Setup.MIN_RECIPE_NAME_LENGTH),))

    image = ImageField(upload_to=Setup.RECIPES_IMAGE_FOLDER,
                       verbose_name='Food photo')

    text = TextField()

    cooking_time = IntegerField(verbose_name='Cooking time, minutes',
                                validators=(
                                    MinValueValidator(
                                        Setup.COOKING_TIME_MIN_VALUE),))

    tag = ManyToManyField(Tag,
                          verbose_name='Tags',
                          related_name='recipes')

    pub_date = DateTimeField(verbose_name='Publication Date',
                             auto_now_add=True,
                             editable=False,)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Recipe'

        verbose_name_plural = 'Recipes'

        ordering = ('-pub_date', )


class RecipeIngredient(Model):
    ingredient = ForeignKey(Ingredient,
                            on_delete=CASCADE,
                            verbose_name='Ingredient',
                            related_name='recipe_ingredients')

    recipe = ForeignKey(Recipe,
                        on_delete=CASCADE,
                        verbose_name='Recipe',
                        related_name='ingredients'
                        )

    amount = FloatField(verbose_name='Ingredient amount',
                        default=1,
                        validators=(
                            BorderedMinValueValidator(
                                limit_value=Setup.INGREDIENT_AMOUNT_MIN_VALUE,
                                is_included=False),
                        ))

    def __str__(self) -> str:
        return self.ingredient.name

    class Meta:
        unique_together = ['ingredient', 'recipe']

        verbose_name = 'Recipe Ingredient'


class Favorites(Model):
    user = ForeignKey(User,
                      on_delete=CASCADE,
                      verbose_name='User',
                      related_name='favorites')

    recipe = ForeignKey(Recipe,
                        related_name='in_favorites',
                        on_delete=CASCADE,
                        verbose_name='Recipe')

    def __str__(self) -> str:
        return f'{self.user.username}_{self.recipe}'

    class Meta:
        ordering = ['user_id']
        verbose_name_plural = 'Favorites'


class ShoppingCart(Model):
    user = ForeignKey(User,
                      on_delete=CASCADE,
                      verbose_name='User',
                      related_name='shopping_carts')

    recipe = ForeignKey(Recipe,
                        on_delete=CASCADE,
                        verbose_name='Recipes',
                        related_name='shopping_carts')

    class Meta:
        ordering = ['user']

        verbose_name = 'Shopping list'

        verbose_name_plural = 'Shopping lists'
