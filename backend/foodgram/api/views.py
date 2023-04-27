
from rest_framework.decorators import action
from django.db.models import Sum
from datetime import datetime
from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import SAFE_METHODS
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DefaultUserViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import (ListAPIView,
                                     CreateAPIView,
                                     DestroyAPIView)
from rest_framework.viewsets import (ReadOnlyModelViewSet,
                                     ModelViewSet,)
from recipes.models import Tag, Ingredient, Recipe, Favorites, ShoppingCart, RecipeIngredient
from api.serializers import (TagSerializer,
                             IngredientSerializer,
                             SubscribeSerializer,
                             GetRecipeSerializer,
                             CreateRecipeSerializer,
                             FavoritesSerializer,
                             ShoppingCartSerializer)
from django_filters.rest_framework import DjangoFilterBackend
from .filters import IngredientFilter, RecipeFilter
from .paginators import PageLimitedPaginator
from .permissions import IsAuthoOrReadOnly
from users.models import Subscribe
from .renders import ShoppingListToPDFRenderer


User = get_user_model()


class UserViewSet(DefaultUserViewSet):

    pagination_class = PageLimitedPaginator

    @action(["get",], detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    pagination_class = PageLimitedPaginator
    permission_classes = (IsAuthoOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return GetRecipeSerializer
        else:
            return CreateRecipeSerializer


class FavoritesView(CreateAPIView, DestroyAPIView):
    serializer_class = FavoritesSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        recipe_id = self.kwargs.get('recipe_id')
        return get_object_or_404(Favorites, recipe=recipe_id, user=self.request.user)

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
        return Subscribe.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        return {"request": self.request}


class SubscribeView(CreateAPIView, DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscribeSerializer

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


class ShoppingCartWithRender(APIView):
    renderer_classes = [ShoppingListToPDFRenderer]

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
        response = Response(shopping_cart,
                            headers={'Content-Disposition':
                                     f'attachment; filename={file_name}'})
        return response
