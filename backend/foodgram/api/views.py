
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.serializers import (CreateRecipeSerializer,
                             FavoritesSerializer,
                             GetRecipeSerializer,
                             IngredientSerializer,
                             ShoppingCartSerializer,
                             SubscribeSerializer,
                             TagSerializer,
                             UserSerializer)
from recipes.models import (Favorites,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)
from users.models import Subscribe
from djoser.conf import settings as djoser_settings
from .filters import IngredientFilter, RecipeFilter
from .paginators import PageLimitedPaginator
from .permissions import IsAuthorOrReadOnly
from .renders import ShoppingListToPDFRenderer


User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    pagination_class = PageLimitedPaginator
    http_method_names = ['get', 'post', ]

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = djoser_settings.PERMISSIONS.current_user
        return super().get_permissions()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get', ]


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    http_method_names = ['get', ]


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.prefetch_related(
        'author', 'ingredients__ingredient').all()
    serializer_class = GetRecipeSerializer
    pagination_class = PageLimitedPaginator
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return GetRecipeSerializer
        else:
            return CreateRecipeSerializer

    def get_serializer_context(self):
        return {"request": self.request}


class FavoritesView(CreateAPIView, DestroyAPIView):
    serializer_class = FavoritesSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        recipe_id = self.kwargs.get('recipe_id')
        return get_object_or_404(Favorites,
                                 recipe=recipe_id,
                                 user=self.request.user)

    def get_serializer(self, *args, **kwargs):
        serializer = self.get_serializer_class()(
            data={'user': self.request.user.id,
                  'recipe': self.kwargs['recipe_id']},
            context={'request': self.request}
        )
        return serializer


class ShoppingCartView(CreateAPIView, DestroyAPIView):
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)

    http_method_names = ('post', 'delete')

    def get_object(self):
        recipe_id = self.kwargs.get('recipe_id')
        favorite_record = get_object_or_404(
            ShoppingCart, recipe=recipe_id, user=self.request.user)
        return favorite_record

    def get_serializer(self, *args, **kwargs):
        serializer = self.get_serializer_class()(
            data={'user': self.request.user.id,
                  'recipe': self.kwargs['recipe_id']},
            context={'request': self.request}
        )
        return serializer


class SubscriptionsView(ListAPIView):
    pagination_class = PageLimitedPaginator
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (Subscribe.objects.
                prefetch_related('subscribe').
                filter(user=self.request.user))

    def get_serializer_context(self):
        return {"request": self.request}


class SubscribeView(CreateAPIView, DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscribeSerializer

    http_method_names = ['post', 'delete']

    def get_object(self):
        subscribe_id = self.kwargs.get('user_id')
        return get_object_or_404(Subscribe,
                                 user=self.request.user,
                                 subscribe__id=subscribe_id)

    def get_serializer(self, *args, **kwargs):
        serializer = self.get_serializer_class()(
            data={'user': self.request.user.id,
                  'subscribe': self.kwargs['user_id']},
            context={'request': self.request}
        )
        return serializer


class ShoppingCartRenderView(APIView):
    renderer_classes = (ShoppingListToPDFRenderer,)
    permission_classes = [IsAuthenticated, ]

    # http_method_names = ['GET']

    def get(self, request, format=None):
        shopping_cart = (RecipeIngredient.
                         objects.
                         all().
                         filter(
                             recipe__shopping_carts__user=request.user).
                         values('ingredient__name',
                                'ingredient__measurement_unit').
                         annotate(total=Sum('amount')))
        file_name = f'Shopping_list_{datetime.now().strftime("%d_%m_%Y")}.pdf'
        response = Response(shopping_cart)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
