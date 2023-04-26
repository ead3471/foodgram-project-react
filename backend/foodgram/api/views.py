
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
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import (ReadOnlyModelViewSet,
                                     ModelViewSet,
                                     GenericViewSet,
                                     )
from rest_framework.mixins import (CreateModelMixin,
                                   ListModelMixin,
                                   DestroyModelMixin)

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
from rest_framework.generics import GenericAPIView
import json
from django.core import serializers
import io
from .reports import create_pdf
from django.http import FileResponse
from users.models import Subscribe


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
    queryset = Recipe.objects.all().order_by('pk')
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

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart_json(self, request):

        shopping_cart = (RecipeIngredient.
                         objects.
                         all().
                         filter(
                             recipe__shopping_carts__user=request.user).
                         values('ingredient__name',
                                'ingredient__measurement_unit').
                         annotate(total=Sum('amount')))
        response = HttpResponse(
            result_json,
            content_type='.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename=shoppings.txt'

        return response

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        file_name = f'ShoppingList_{datetime.now().strftime("%m_%d_%Y_%H:%M")}.pdf'
        shopping_cart = (RecipeIngredient.
                         objects.
                         all().
                         filter(
                             recipe__shopping_carts__user=request.user).
                         values('ingredient__name',
                                'ingredient__measurement_unit').
                         annotate(total=Sum('amount')))

        pdf = create_pdf(ingredients=shopping_cart)
        pdf.seek(0)
        responce = FileResponse(
            pdf,
            filename=file_name,
            content_type='application/pdf')

        return responce


class FavoritesView(CreateModelMixin, DestroyModelMixin, GenericAPIView):
    serializer_class = FavoritesSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        recipe_id = self.kwargs.get('recipe_id')

        favorite_record = get_object_or_404(
            Favorites, recipe=recipe_id, user=self.request.user)
        return favorite_record

    def delete(self, request, *args, **kwargs):
        return self.destroy(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {'recipe_id': kwargs['recipe_id'],
                'user': self.request.user}
        serializer = self.get_serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartView(ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericAPIView):
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        recipe_id = self.kwargs.get('recipe_id')

        favorite_record = get_object_or_404(
            ShoppingCart, recipe=recipe_id, user=self.request.user)
        return favorite_record

    def delete(self, request, *args, **kwargs):
        return self.destroy(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {'recipe_id': kwargs['recipe_id'],
                'user': self.request.user}
        serializer = self.get_serializer_class()(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsView(ListAPIView):
    pagination_class = PageLimitedPaginator
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Subscribe.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        return {"request": self.request}


class SubscribeView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscribeSerializer

    def delete(self, request, user_id):
        subscription = get_object_or_404(
            Subscribe, user=request.user, subscribe__pk=user_id)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, user_id):
        print(request.GET)
        print(request.GET.get('recipes_limit'))
        data = {'user': self.request.user.id,
                'subscribe': user_id}
        serializer = SubscribeSerializer(
            data=data, context={'request': self.request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
