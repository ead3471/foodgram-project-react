from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from api.views import (UserViewSet,
                       TagViewSet,
                       IngredientViewSet,
                       RecipeViewSet,
                       FavoritesView,
                       ShoppingCartView,
                       SubscribeView,
                       SubscriptionsView,
                       ShoppingCartWithRender)

router_api = DefaultRouter()
router_api.register(r'users', UserViewSet)
router_api.register(r'tags', TagViewSet)
router_api.register(r'ingredients', IngredientViewSet)
router_api.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/', include('djoser.urls.authtoken')),

    path(r'api/recipes/download_shopping_cart/',
         ShoppingCartWithRender.as_view(), name='shopping_cart'),

    path('api/', include(router_api.urls)),

    path(r'api/recipes/<recipe_id>/favorite/',
         FavoritesView.as_view(), name='favorite'),

    path(r'api/recipes/<recipe_id>/shopping_cart/',
         ShoppingCartView.as_view(), name='shopping_cart'),

    path(r'api/users/<user_id>/subscribe/',
         SubscribeView.as_view(), name='subscribe'),

    path(r'api/users/subscriptions',
         SubscriptionsView.as_view(), name='subscriptions'),

]
