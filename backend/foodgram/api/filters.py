
from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        field_name='name', lookup_expr='istartswith')

    class Meta():
        model = Ingredient
        fields = ['name', ]


class RecipeFilter(FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart')
    tags = filters.ModelMultipleChoiceFilter(field_name='tag__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all())

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset

    class Meta():
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart', 'tags')
