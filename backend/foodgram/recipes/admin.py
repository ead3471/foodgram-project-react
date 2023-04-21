from django.contrib import admin
from .models import *

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingridient)
admin.site.register(ShopingCart)
admin.site.register(Favorites)
admin.site.register(RecipeIngridient)
