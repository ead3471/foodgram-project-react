from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline, register
from .models import *


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color')


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measure_unit')
    search_fields = ('name', 'measure_unit')
    list_filter = ('name',)


class RecipeIngredientInline(TabularInline):
    model = RecipeIngredient
    extra = 1


@register(RecipeIngredient)
class RecipeIngredientAdmin(ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')
    search_fields = ('ingredient', 'recipe')
    list_filter = ('ingredient',)


@register(ShopingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user',)


@register(Favorites)
class FavoritesAdmin(ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user',)


@register(Recipe)
class RecipiesAdmin(ModelAdmin):
    readonly_fields = ('in_favorites_count',)

    inlines = (RecipeIngredientInline,)

    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tag')

    def in_favorites_count(self, recipe: Recipe):
        return recipe.in_favorites.count()

    in_favorites_count.short_description = 'Number of adds to favorites'
