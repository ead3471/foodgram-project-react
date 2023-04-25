from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline, register, StackedInline, display
from .models import *
from django.utils.html import format_html


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'colored_cell', 'slug')
    search_fields = ('name', 'color')

    @display(description='Color')
    def colored_cell(self, obj: Tag):
        return format_html(
            '<span style="color:{};"><b>{}<b></span>',
            obj.color,
            obj.color
        )


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name',)


class RecipeIngredientInline(TabularInline):
    model = RecipeIngredient
    # fields = ('ingredient_name', 'amount')
    extra = 1


@register(RecipeIngredient)
class RecipeIngredientAdmin(ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')
    search_fields = ('ingredient', 'recipe')
    list_filter = ('ingredient',)


@register(ShoppingCart)
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
