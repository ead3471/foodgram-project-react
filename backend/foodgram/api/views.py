
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from djoser.views import UserViewSet as DefaultViewSet
from .serializers import UserSerializer
from .permisions import UserPermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserViewSet(DefaultViewSet):

    @action(["get",], detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)
