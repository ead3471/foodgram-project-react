
from rest_framework.decorators import action
from django.contrib.auth import get_user_model

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import SAFE_METHODS
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DefaultUserViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, GenericViewSet
from rest_framework.mixins import (CreateModelMixin,
                                   ListModelMixin,
                                   DestroyModelMixin,
                                   )

from recipes.models import Tag, Ingredient, Recipe, Favorites, ShoppingCart
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


User = get_user_model()


class UserViewSet(DefaultUserViewSet):

    pagination_class = PageLimitedPaginator

    @action(["get",], detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        methods=['post',],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='(?P<subscribe_user_id>[^/.]+)/subscribe'
    )
    def subscribe(self, request, subscribe_user_id: int):
        subscribe_user = get_object_or_404(User, subscribe_user_id)
        serialiser = SubscribeSerializer(
            user=self.request.user, subscribe=subscribe_user)
        serialiser.save()
        return Response(serialiser.data, status=status.HTTP_200_OK)


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
    )
    def download_shopping_cart(self, request):
        pass


class FavoritesView(CreateModelMixin, DestroyModelMixin, GenericAPIView):
    queryset = Favorites.objects.all()
    serializer_class = FavoritesSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'delete']

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
        serializer = FavoritesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartView(ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericAPIView):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'delete']

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
        serializer = ShoppingCartSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
