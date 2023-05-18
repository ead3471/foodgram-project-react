import shutil
import tempfile
from django.conf import settings
from django.test import TestCase, override_settings
from rest_framework.test import APIClient as Client
from django.contrib.auth import get_user_model
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from users.models import Subscribe
from rest_framework import status
from rest_framework.authtoken.models import Token
from .json_api_schemas import (
    RECIPE_RESPONSE_JSON_SCHEMA,
    RECIPES_PAGINATED_RESPONCE_JSON_SCHEMA,
)
from .utils import (
    create_image,
    authorize_client_by_user,
    get_byte_64_image,
    test_recipe_content,
    test_json_schema,
)
from django.urls import reverse
from api.serializers import (
    IngredientSerializer,
    TagSerializer,
    UserSerializer,
    SubscribeSerializer,
)
import json

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)


User = get_user_model()


# TODO 1. Change tests to not using serializers
# TODO 2. Add checking jsonschema
# TODO 3. Add checking creating Recipe,with bas parameters


class TestIngredientsView(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.ingredient = Ingredient.objects.create(
            name="name", measurement_unit="unit"
        )

    def test_list(self):
        response_data = self.client.get(reverse("ingredients-list")).data

        expected_data = IngredientSerializer(
            Ingredient.objects.all(), many=True
        ).data
        self.assertEqual(response_data, expected_data)

    def test_retrive(self):
        response_data = self.client.get(
            reverse(
                "ingredients-detail",
                kwargs={"pk": TestIngredientsView.ingredient.pk},
            )
        ).data

        expected_data = IngredientSerializer(
            instance=TestIngredientsView.ingredient
        ).data
        self.assertEqual(response_data, expected_data)


class TestTagsView(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.tag = Tag.objects.create(name="name", slug="slug", color="#FFFFFF")

    def test_list(self):
        response_data = self.client.get(reverse("tags-list")).data
        expected_data = TagSerializer(Tag.objects.all(), many=True).data
        self.assertEqual(response_data, expected_data)

    def test_retrive(self):
        response_data = self.client.get(
            reverse("tags-detail", kwargs={"pk": TestTagsView.tag.pk})
        ).data

        expected_data = TagSerializer(instance=TestTagsView.tag).data
        self.assertEqual(response_data, expected_data)


class TestUsersView(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user_1 = User.objects.create(
            email="some-email@email.com", username="user_name"
        )

        user_1_token = Token.objects.create(user=cls.user_1)
        user_1_client = Client()
        user_1_client.credentials(
            HTTP_AUTHORIZATION="Token " + user_1_token.key
        )
        cls.user_1_client = user_1_client

        cls.author_user = User.objects.create(
            email="some-author-email@email.com", username="author_name"
        )

    def test_list(self):
        client = Client()
        response_data = client.get(reverse("user-list")).data
        expected_data = UserSerializer(User.objects.all(), many=True).data
        self.assertEqual(response_data, expected_data)

    def test_retrive(self):
        response_data = self.client.get(
            reverse("user-detail", kwargs={"id": TestUsersView.user_1.id})
        ).data

        expected_data = UserSerializer(instance=TestUsersView.user_1).data
        self.assertEqual(response_data, expected_data)

    def test_me(self):
        response_data = TestUsersView.user_1_client.get(
            reverse("user-me")
        ).data
        expected_data = UserSerializer(instance=TestUsersView.user_1).data
        self.assertEqual(response_data, expected_data)

    def test_register_new_user(self):
        client = Client()
        reg_data = {
            "username": "new_user",
            "email": "some@email.com",
            "password": "Aa123456789",
            "first_name": "some_name",
            "last_name": "some_name",
        }
        client.post(reverse("user-list"), data=reg_data)
        self.assertTrue(User.objects.filter(email=reg_data["email"]).exists())


class TestSubscribeView(TestCase):
    def setUp(self) -> None:
        self.user_1 = User.objects.create(
            email="some-email@email.com", username="some_name"
        )

        user_1_token = Token.objects.create(user=self.user_1)
        user_1_client = Client()
        user_1_client.credentials(
            HTTP_AUTHORIZATION="Token " + user_1_token.key
        )
        self.user_1_client = user_1_client

        self.author_user = User.objects.create(
            email="some-author-email@email.com", username="author_name"
        )

    def test_create_subscribe(self):
        self.user_1_client.post(
            reverse("subscribe", kwargs={"user_id": self.author_user.pk})
        )
        self.assertTrue(
            Subscribe.objects.filter(
                user=self.user_1, subscribe=self.author_user
            ).exists()
        )

    def test_remove_subscribe(self):
        Subscribe.objects.create(user=self.user_1, subscribe=self.author_user)
        self.assertTrue(
            Subscribe.objects.filter(
                user=self.user_1, subscribe=self.author_user
            ).exists()
        )
        self.user_1_client.delete(
            reverse("subscribe", kwargs={"user_id": self.author_user.pk})
        )
        self.assertFalse(
            Subscribe.objects.filter(
                user=self.user_1, subscribe=self.author_user
            ).exists()
        )

    def test_subscriptions_list(self):
        resp = self.user_1_client.get(reverse("subscriptions"))
        expected_data = SubscribeSerializer(
            Subscribe.objects.filter(
                user=self.user_1, subscribe=self.author_user
            ),
            many=True,
        ).data
        self.assertEqual(resp.data, expected_data)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestRecipeView(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author_user = User.objects.create(
            email="some@email.com", username="some_name"
        )

        cls.usual_user = User.objects.create(
            email="some1@email.com", username="some_name1"
        )

        cls.ingredients = (
            Ingredient.objects.create(
                name="ingr_1", measurement_unit="units_1"
            ),
            Ingredient.objects.create(
                name="ingr_2", measurement_unit="units_2"
            ),
        )

        cls.tags = [
            Tag.objects.create(name="tag_1", color="#FFFFFF", slug="tag_1"),
            Tag.objects.create(name="tag_2", color="#FF00FF", slug="tag_2"),
        ]

        cls.test_recipe = Recipe.objects.create(
            author=cls.author_user,
            name="test recipe",
            text="some_text",
            image=create_image(),
            cooking_time=2,
        )

        cls.recipe_ingredients = [
            RecipeIngredient.objects.create(
                recipe=cls.test_recipe, ingredient=ingredient, amount=count
            )
            for count, ingredient in enumerate(cls.ingredients)
        ]

        cls.test_recipe.tag.set(cls.tags)
        cls.test_recipe.ingredients.set(cls.recipe_ingredients)

    def setUp(self) -> None:
        self.author_client = Client()
        authorize_client_by_user(
            self.author_client, TestRecipeView.author_user
        )

        self.usual_client = Client()
        authorize_client_by_user(self.usual_client, TestRecipeView.usual_user)

    def test_recipe_creation(self):
        recipe_data = {
            "name": "recipe_name",
            "text": "some_text",
            "cooking_time": 1,
            "tags": list(map(lambda v: v.pk, TestRecipeView.tags)),
            "ingredients": [
                {"id": ingredient.id, "amount": count}
                for count, ingredient in enumerate(
                    TestRecipeView.ingredients, start=1
                )
            ],
            "image": get_byte_64_image(),
        }

        # check given recipe is not exists before post request
        self.assertFalse(
            Recipe.objects.filter(
                name=recipe_data["name"],
                text=recipe_data["text"],
                cooking_time=recipe_data["cooking_time"],
            ).exists()
        )

        response = self.author_client.post(
            reverse("recipe-list"),
            data=json.dumps(recipe_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check given recipe is exists after post request
        self.assertTrue(
            Recipe.objects.filter(
                name=recipe_data["name"],
                text=recipe_data["text"],
                cooking_time=recipe_data["cooking_time"],
            ).exists()
        )

        test_json_schema(self, RECIPE_RESPONSE_JSON_SCHEMA, response.data)

    def test_recipe_delete_by_author(self):
        response = self.author_client.delete(
            reverse(
                "recipe-detail", kwargs={"pk": TestRecipeView.test_recipe.pk}
            )
        )
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertFalse(
            Recipe.objects.filter(pk=TestRecipeView.test_recipe.pk).exists(),
            "The recipe is not removed",
        )

    def test_recipe_delete_by_not_author(self):
        response = self.usual_client.delete(
            reverse(
                "recipe-detail", kwargs={"pk": TestRecipeView.test_recipe.pk}
            )
        )
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertTrue(
            Recipe.objects.filter(pk=TestRecipeView.test_recipe.pk).exists(),
            "The recipe is removed by not author",
        )

    def test_non_existent_recipe_delete(self):
        recipes_count_before_delete = Recipe.objects.count()
        response = self.usual_client.delete(
            reverse(
                "recipe-detail",
                kwargs={"pk": TestRecipeView.test_recipe.pk + 10000},
            )
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        recipes_count_after_delete = Recipe.objects.count()
        self.assertEqual(
            recipes_count_before_delete, recipes_count_after_delete
        )

    def test_recipes_list(self):
        response = self.usual_client.get(
            reverse("recipe-list"), data={"limit": 1}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        test_json_schema(
            self, RECIPES_PAGINATED_RESPONCE_JSON_SCHEMA, response.data
        )

    def test_recipe_detail(self):
        response = self.usual_client.get(
            reverse(
                "recipe-detail", kwargs={"pk": TestRecipeView.test_recipe.pk}
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        test_json_schema(self, RECIPE_RESPONSE_JSON_SCHEMA, response.data)

    def test_non_existent_recipe_detail(self):
        response = self.usual_client.get(
            reverse(
                "recipe-detail",
                kwargs={"pk": TestRecipeView.test_recipe.pk + 10000},
            )
        )
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_recipe_update(self):
        new_recipe_data = {
            "name": "new_recipe_name",
            "text": "new_some_text",
            "cooking_time": 4,
            "tags": [
                TestRecipeView.tags[0].pk,
            ],
            "ingredients": [
                {"id": TestRecipeView.ingredients[0].pk, "amount": 1000.0}
            ],
            "image": get_byte_64_image(),
        }

        response = self.author_client.patch(
            reverse(
                "recipe-detail", kwargs={"pk": TestRecipeView.test_recipe.pk}
            ),
            data=json.dumps(new_recipe_data),
            content_type="application/json",
        )
        test_json_schema(self, RECIPE_RESPONSE_JSON_SCHEMA, response.data)

        changed_recipe = Recipe.objects.get(pk=TestRecipeView.test_recipe.pk)
        test_recipe_content(self, new_recipe_data, changed_recipe)
