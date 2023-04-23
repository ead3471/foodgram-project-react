from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import Subscribe
from django.shortcuts import get_object_or_404
from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            Favorites,
                            ShopingCart)

from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth.models import AnonymousUser


User = get_user_model()


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'id',
            'is_subscribed'
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj):
        return True


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeDescriptionSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'coocking_time')
        read_only_fields = '__all__'


class RecipeSerializer(ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients')
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_card = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('author', 'name', 'tags', 'ingredients',
                  'image', 'text', 'cooking_time', 'is_favorited', 'is_in_shopping_card')

    def get_is_favorited(self, recipe):
        current_user = self.context['request'].user
        print(type(current_user))
        if current_user.is_anonymous:
            return False
        else:
            return current_user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_card(self, recipe):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        else:
            return current_user.purchases.filter(recipe=recipe).exists()


class SubscribeSerializer(ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ['user', 'subscribe']

    def validate(self, attrs):
        print(str(attrs))
        return super().validate(attrs)

    def validate_subscribe(self, user_id: int):
        print(self.context.get('request').query_params.get('recipes_limit', None))

        subscribe_user = get_object_or_404(User, user_id)
        current_user = self.context.get('request').user
        if current_user == subscribe_user:
            raise ValidationError("Subscribe to yourself is prohbited!")

        if (Subscribe.
            objects.
            filter(user=current_user).
                filter(subscribe=subscribe_user).exists()):
            raise ValidationError("Follow already exists!")
        return user_id
