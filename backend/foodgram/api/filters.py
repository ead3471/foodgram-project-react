import django_filters
from django_filters import rest_framework as filters
from recipes.models import Ingredient


class IngredientFilter(django_filters.FilterSet):
    name = filters.CharFilter(
        field_name='name', lookup_expr='istartswith')

    class Meta():
        model = Ingredient
        fields = ['name',]
