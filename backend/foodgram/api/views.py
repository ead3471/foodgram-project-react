
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
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.mixins import (CreateModelMixin,
                                   ListModelMixin,
                                   DestroyModelMixin)

from recipes.models import Tag, Ingredient, Recipe, Favorites, ShopingCart
from api.serializers import (TagSerializer,
                             IngredientSerializer,
                             SubscribeSerializer,
                             GetRecipeSerializer,
                             CreateRecipeSerializer)
from django_filters.rest_framework import DjangoFilterBackend
from .filters import IngredientFilter, RecipeFilter
from .paginators import PageLimitedPaginator
from .permissions import IsAuthoOrReadOnly


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

        return super().get_serializer_class()
