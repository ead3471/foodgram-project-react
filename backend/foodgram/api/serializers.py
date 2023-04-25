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


class GetRecipeIngredientSerializer(ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.pk')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateRecipeIngredientSerializer(ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeDescriptionSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'coocking_time')
        read_only_fields = '__all__'


class GetRecipeSerializer(ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, source='tag')
    ingredients = GetRecipeIngredientSerializer(many=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_card = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'tags', 'ingredients',
                  'image', 'text', 'cooking_time', 'is_favorited', 'is_in_shopping_card')

    def get_is_favorited(self, recipe):
        if self.context.get('request') is None:
            return False

        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        else:
            return current_user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_card(self, recipe):
        if self.context.get('request') is None:
            return False

        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        else:
            return current_user.shopping_carts.filter(recipe=recipe).exists()


class CreateRecipeSerializer(ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    ingredients = CreateRecipeIngredientSerializer(many=True)
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = ('name', 'ingredients',
                  'image', 'text', 'cooking_time', 'tags')

    def to_representation(self, instance):
        return GetRecipeSerializer(instance).data

    def create_new_ingredients(self, new_recipe, new_ingredients):
        ingredients = [
            RecipeIngredient(
                recipe=new_recipe,
                ingredient=ingredient["id"],
                amount=ingredient["amount"])
            for ingredient in new_ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):

        tags = validated_data.pop('tags')
        request_user = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        new_recipe = Recipe.objects.create(author=request_user,
                                           **validated_data)

        self.create_new_ingredients(new_recipe, ingredients)
        new_recipe.tag.add(*tags)
        return new_recipe

    def update(self, instance: Recipe, validated_data):
        instance.ingredients.filter(recipe=instance).delete()
        self.create_new_ingredients(instance,
                                    validated_data.pop('ingredients'))

        tags = validated_data.pop('tags')
        instance.tag.set(tags, clear=True)

        return super().update(instance, validated_data)

    def validate(self, data):
        new_ingredints_in_recipe: dict[str, str] = data['ingredients']
        if len(set([value['id'] for value in new_ingredints_in_recipe])) != len(new_ingredints_in_recipe):
            raise ValidationError(
                'The ingredients list should not contain the same elements')
        return super().validate(data)


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


class FavoritesSerializer(ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = serializers.CharField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorites
        fields = ('id', 'cooking_time', 'image', 'name')

    # def get_recipe_id(self, favorite):
    #     return self.context.get['recipe_id']

    # def get_user_id(self, favorite):
    #     return self.context.get['request'].user

    def validate(self, attrs):
        recipe_id = self.initial_data['recipe_id']
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        request_user = self.initial_data['user']

        if Favorites.objects.all().filter(recipe__id=recipe_id).filter(user=request_user).exists():
            raise ValidationError('Already added to favorites!')

        attrs['user'] = request_user
        attrs['recipe'] = recipe
        return super().validate(attrs)

    def create(self, validated_data):
        print(validated_data)
        return Favorites.objects.create(user=validated_data['user'], recipe=validated_data['recipe'])
