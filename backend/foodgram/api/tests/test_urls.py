import shutil
import tempfile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient as Client
from django.contrib.auth import get_user_model
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from rest_framework import status
from typing import Callable
from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from django.conf import settings
from .utils import create_image

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class URLsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author_1 = User.objects.create(
            email="some@some.com", username="some_name_1"
        )
        cls.user_1 = User.objects.create(
            email="some1@some1.com", username="some_name_2"
        )

        cls.tag = Tag.objects.create(
            name="test_tag_1", slug="test_tag_1", color="#FFFFFF"
        )

        cls.ingredient = Ingredient.objects.create(
            name="name", measurement_unit="unit"
        )

        cls.recipe = Recipe.objects.create(
            author=URLsTests.author_1,
            name="recipe_name",
            image=create_image(),
            text="some_text",
            cooking_time=1,
        )

        cls.recipe.tag.set((cls.tag,))

        cls.recipe_ingredient = RecipeIngredient(
            ingredient=cls.ingredient, amount=2, recipe=cls.recipe
        )

    def setUp(self) -> None:
        super().setUp()
        self.anon_client = Client()

        self.user_1_client = Client()
        user_1_token = Token.objects.create(user=URLsTests.user_1)
        self.user_1_client.credentials(
            HTTP_AUTHORIZATION="Token " + user_1_token.key
        )

        self.author_client = Client()
        author_token = Token.objects.create(user=URLsTests.author_1)
        self.author_client.credentials(
            HTTP_AUTHORIZATION="Token " + author_token.key
        )

    def test_anauth_user_urls_access(self):
        client = self.anon_client

        get = client.get
        post = client.post
        delete = client.delete
        patch = client.patch
        put = client.put

        all_check_methods = [
            client.get,
            client.put,
            client.post,
            client.delete,
            client.patch,
        ]

        urls: dict[str, dict[Callable, int]] = {
            "/api/users/me/": {
                post: status.HTTP_405_METHOD_NOT_ALLOWED,
            },
            "/api/users/": {
                get: status.HTTP_200_OK,
                post: status.HTTP_400_BAD_REQUEST,
                delete: status.HTTP_405_METHOD_NOT_ALLOWED,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED,
            },
            f"/api/users/{URLsTests.author_1.pk}/": {
                get: status.HTTP_200_OK,
                post: status.HTTP_405_METHOD_NOT_ALLOWED,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED,
            },
            "/api/users/set_password/": {
                get: status.HTTP_405_METHOD_NOT_ALLOWED,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                delete: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED,
            },
            "/api/auth/token/login/": {
                post: status.HTTP_400_BAD_REQUEST,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                get: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED,
                delete: status.HTTP_405_METHOD_NOT_ALLOWED,
            },
            "/api/auth/token/logout/": {},
            f"/api/users/{URLsTests.author_1.pk}/subscribe/": {},
            "/api/tags/": {
                get: status.HTTP_200_OK,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                delete: status.HTTP_405_METHOD_NOT_ALLOWED,
                post: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED,
            },
            f"/api/tags/{URLsTests.tag.pk}/": {
                get: status.HTTP_200_OK,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                delete: status.HTTP_405_METHOD_NOT_ALLOWED,
                post: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED,
            },
            "/api/recipes/": {
                get: status.HTTP_200_OK,
            },
            f"/api/recipes/{URLsTests.recipe.pk}/": {get: status.HTTP_200_OK},
            "/api/recipes/download_shopping_cart/": {},
            f"/api/recipes/{URLsTests.recipe.pk}/shopping_cart/": {},
            f"/api/recipes/{URLsTests.recipe.pk}/favorite/": {},
            "/api/users/subscriptions/": {},
            "/api/ingredients/": {
                get: status.HTTP_200_OK,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                delete: status.HTTP_405_METHOD_NOT_ALLOWED,
                post: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED,
            },
            f"/api/ingredients/{URLsTests.ingredient.pk}/": {
                get: status.HTTP_200_OK,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                delete: status.HTTP_405_METHOD_NOT_ALLOWED,
                post: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED,
            },
        }

        for url, methods_dict in urls.items():
            for http_method in all_check_methods:
                with self.subTest(url=url, method=http_method.__name__):
                    expected_status = methods_dict.get(
                        http_method, status.HTTP_401_UNAUTHORIZED
                    )
                    response: HttpResponse = http_method(url)
                    self.assertEqual(expected_status, response.status_code)

    def test_auth_user_urls_access(self):
        auth_client = self.user_1_client

        get = auth_client.get
        post = auth_client.post
        delete = auth_client.delete
        patch = auth_client.patch
        put = auth_client.put

        all_check_methods = [get, put, post, delete, patch]
        default_responce_status = status.HTTP_405_METHOD_NOT_ALLOWED

        urls: dict[str, dict[Callable, int]] = {
            "/api/users/": {
                get: status.HTTP_200_OK,
                post: status.HTTP_400_BAD_REQUEST,
            },
            f"/api/users/{URLsTests.author_1.pk}/": {
                get: status.HTTP_200_OK,
            },
            f"/api/users/{URLsTests.author_1.pk}/subscribe/": {
                post: status.HTTP_201_CREATED,
                delete: status.HTTP_204_NO_CONTENT,
            },
            "/api/users/subscriptions/": {
                get: status.HTTP_200_OK,
            },
            "/api/users/me/": {
                get: status.HTTP_200_OK,
            },
            "/api/tags/": {
                get: status.HTTP_200_OK,
            },
            f"/api/tags/{URLsTests.tag.pk}/": {
                get: status.HTTP_200_OK,
            },
            "/api/recipes/": {
                get: status.HTTP_200_OK,
                post: status.HTTP_400_BAD_REQUEST,
            },
            f"/api/recipes/{URLsTests.recipe.pk}/": {
                get: status.HTTP_200_OK,
                put: status.HTTP_403_FORBIDDEN,
                delete: status.HTTP_403_FORBIDDEN,
                patch: status.HTTP_403_FORBIDDEN,
            },
            "/api/recipes/download_shopping_cart/": {
                get: status.HTTP_200_OK,
            },
            f"/api/recipes/{URLsTests.recipe.pk}/shopping_cart/": {
                post: status.HTTP_201_CREATED,
                delete: status.HTTP_204_NO_CONTENT,
            },
            f"/api/recipes/{URLsTests.recipe.pk}/favorite/": {
                post: status.HTTP_201_CREATED,
                delete: status.HTTP_204_NO_CONTENT,
            },
            "/api/ingredients/": {
                get: status.HTTP_200_OK,
            },
            f"/api/ingredients/{URLsTests.ingredient.pk}/": {
                get: status.HTTP_200_OK,
            },
            "/api/auth/token/login/": {
                post: status.HTTP_400_BAD_REQUEST,
            },
            "/api/auth/token/logout/": {
                post: status.HTTP_204_NO_CONTENT,
                delete: status.HTTP_401_UNAUTHORIZED,
                patch: status.HTTP_401_UNAUTHORIZED,
            },
        }

        for url, methods_dict in urls.items():
            for http_method in all_check_methods:
                with self.subTest(url=url, method=http_method.__name__):
                    expected_status = methods_dict.get(
                        http_method, default_responce_status
                    )
                    response: HttpResponse = http_method(url)
                    self.assertEqual(expected_status, response.status_code)
