
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from djoser.views import UserViewSet as DefaultUserViewSet
from .serializers import UserSerializer
from .permisions import UserPermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.authtoken.models import Token
from rest_framework.mixins import (CreateModelMixin,
                                   ListModelMixin,
                                   DestroyModelMixin)
from rest_framework.viewsets import GenericViewSet
from .serializers import SubscribeSerializer
from users.models import Subscribe
from recipes.models import Tag, Ingredient
from api.serializers import TagSerializer, IngredientSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import IngredientFilter
from .paginators import PageLimitedPaginator

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
