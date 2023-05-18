from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscribe

User = get_user_model()


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "id",
            "is_subscribed",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def get_is_subscribed(self, user_obj):
        context = self.context.get("request")
        if context and context.user.is_authenticated:
            return Subscribe.objects.filter(
                user=context.user, subscribe=user_obj
            ).exists()
        return False


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class GetRecipeIngredientSerializer(ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.pk")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class CreateRecipeIngredientSerializer(ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeDescriptionSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class GetRecipeSerializer(ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, source="tag")
    ingredients = GetRecipeIngredientSerializer(many=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "name",
            "tags",
            "ingredients",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )
        read_only_fields = ("id",)

    def get_is_favorited(self, recipe):
        if self.context.get("request") is None:
            return False

        current_user = self.context["request"].user
        if current_user.is_anonymous:
            return False
        else:
            return current_user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        if self.context.get("request") is None:
            return False

        current_user = self.context["request"].user
        if current_user.is_anonymous:
            return False
        else:
            return current_user.shopping_carts.filter(recipe=recipe).exists()


class CreateRecipeSerializer(ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = CreateRecipeIngredientSerializer(many=True)
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            "name",
            "ingredients",
            "image",
            "text",
            "cooking_time",
            "tags",
        )

    def to_representation(self, instance):
        return GetRecipeSerializer(instance, context=self.context).data

    def create_new_ingredients(self, new_recipe, new_ingredients):
        ingredients = [
            RecipeIngredient(
                recipe=new_recipe,
                ingredient=ingredient["id"],
                amount=ingredient["amount"],
            )
            for ingredient in new_ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        request_user = self.context["request"].user
        ingredients = validated_data.pop("ingredients")
        new_recipe = Recipe.objects.create(
            author=request_user, **validated_data
        )

        self.create_new_ingredients(new_recipe, ingredients)
        new_recipe.tag.add(*tags)
        return new_recipe

    def update(self, instance: Recipe, validated_data):
        instance.ingredients.filter(recipe=instance).delete()
        self.create_new_ingredients(
            instance, validated_data.pop("ingredients")
        )

        tags = validated_data.pop("tags")
        instance.tag.set(tags, clear=True)

        return super().update(instance, validated_data)

    def validate(self, data):
        new_ingredints_in_recipe: dict[str, str] = data["ingredients"]
        unique_elements_number = len(
            set([value["id"] for value in new_ingredints_in_recipe])
        )
        if unique_elements_number != len(new_ingredints_in_recipe):
            raise ValidationError(
                "The ingredients list should not contain the same elements"
            )
        return super().validate(data)


class SubscribeSerializer(ModelSerializer):
    email = serializers.ReadOnlyField(source="subscribe.email")
    id = serializers.ReadOnlyField(source="subscribe.id")
    username = serializers.ReadOnlyField(source="subscribe.username")
    first_name = serializers.ReadOnlyField(source="subscribe.first_name")
    last_name = serializers.ReadOnlyField(source="subscribe.last_name")
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscribe
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "recipes",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "user",
            "subscribe",
        )
        extra_kwargs = {
            "user": {"write_only": True},
            "subscribe": {"write_only": True},
        }

    def get_is_subscribed(self, subscribe_obj: Subscribe):
        return True

    def get_recipes_count(self, subscribe_obj: Subscribe):
        return subscribe_obj.subscribe.recipes.count()

    def get_recipes(self, subscribe_obj: Subscribe):
        limit = self.context["request"].GET.get("recipes_limit")
        if limit:
            recipes = Recipe.objects.filter(author=subscribe_obj.subscribe)[
                : int(limit)
            ]
        else:
            recipes = Recipe.objects.filter(author=subscribe_obj.subscribe)
        serializer = RecipeDescriptionSerializer(recipes, many=True)
        return serializer.data

    def validate(self, attrs):
        current_user = attrs["user"]
        subscribe_user = attrs["subscribe"]
        limit = self.context["request"].GET.get("recipes_limit")
        if limit is not None:
            if not limit.isnumeric():
                raise ValidationError("recipes_limit must be a number!")

        if Subscribe.objects.filter(
            user=current_user, subscribe=subscribe_user
        ).exists():
            raise ValidationError("This subscription is already registered")

        if subscribe_user == current_user:
            raise ValidationError("Subscribing to yourself is not allowed!")

        return attrs


class FavoritesSerializer(ModelSerializer):
    id = serializers.ReadOnlyField(source="recipe.id")
    name = serializers.CharField(source="recipe.name", read_only=True)
    image = serializers.CharField(source="recipe.image", read_only=True)
    cooking_time = serializers.ReadOnlyField(source="recipe.cooking_time")

    class Meta:
        model = Favorites
        fields = ("id", "cooking_time", "image", "name", "recipe", "user")
        extra_kwargs = {
            "user": {"write_only": True},
            "recipe": {"write_only": True},
        }

    def validate(self, attrs):
        user = attrs["user"]
        recipe = attrs["recipe"]

        if Favorites.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError("Already added to favorites!")
        return attrs


class ShoppingCartSerializer(ModelSerializer):
    id = serializers.ReadOnlyField(source="recipe.id")
    name = serializers.CharField(source="recipe.name", read_only=True)
    image = serializers.CharField(source="recipe.image", read_only=True)
    cooking_time = serializers.ReadOnlyField(source="recipe.cooking_time")

    class Meta:
        model = ShoppingCart
        fields = ("id", "cooking_time", "image", "name", "recipe", "user")
        extra_kwargs = {
            "user": {"write_only": True},
            "recipe": {"write_only": True},
        }

    def validate(self, attrs):
        recipe = attrs["recipe"]
        user = attrs["user"]

        if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError("Already added to shopping cart!")

        return attrs
