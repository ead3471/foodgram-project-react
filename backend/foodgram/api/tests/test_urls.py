from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from users.models import Subscribe
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from typing import Callable, Dict
from django.http import HttpResponse

User = get_user_model()


class URLsTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author_1 = User.objects.create(email='some@some.com',
                                           username='some_name_1')

        cls.tag = Tag.objects.create(name='test_tag_1',
                                     slug='test_tag_1',
                                     color='#FFFFFF')
        cls.ingredient = Ingredient.objects.create(name='name',
                                                   measurement_unit='unit')

        cls.recipe = Recipe.objects.create(author=URLsTests.author_1,
                                           name='recipe_name',
                                           image=URLsTests.create_image(),
                                           text='some_text',
                                           cooking_time=1)
        recipe_ingredient = RecipeIngredient(
            ingredient=cls.ingredient,
            amount=2,
            recipe=cls.recipe
        )

        cls.recipe.tag.set((cls.tag,))

    def create_image() -> SimpleUploadedFile:
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        return SimpleUploadedFile(
            'small.gif', small_gif, content_type='image/gif')

    def setUp(self) -> None:
        super().setUp()
        self.anon_user = Client()

    def test_get_anauth_user_urls_access(self):
        client = self.client
        get = client.get
        post = client.post
        delete = client.delete
        patch = client.patch
        put = client.put

        all_check_methods = [get, put, post, delete, patch]

        urls: dict[str, dict[Callable, int]] = {
            "/api/users/": {
                get: status.HTTP_200_OK,
                post: status.HTTP_400_BAD_REQUEST,
                delete: status.HTTP_405_METHOD_NOT_ALLOWED,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED},

            f"/api/users/{URLsTests.author_1.pk}/": {
                get: status.HTTP_200_OK,
                post: status.HTTP_405_METHOD_NOT_ALLOWED,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED},

            f"/api/users/{URLsTests.author_1.pk}/subscribe/": {},

            "/api/users/me/": {},

            "/api/tags/": {
                get: status.HTTP_200_OK,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                delete: status.HTTP_405_METHOD_NOT_ALLOWED,
                post: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED},

            f"/api/tags/{URLsTests.tag.pk}/": {
                get: status.HTTP_200_OK,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                delete: status.HTTP_405_METHOD_NOT_ALLOWED,
                post: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED},

            "/api/recipes/": {
                get: status.HTTP_200_OK, },

            f"/api/recipes/{URLsTests.recipe.pk}/": {
                get: status.HTTP_200_OK,
                post: status.HTTP_401_UNAUTHORIZED},

            f"/api/recipes/download_shopping_cart/": {},

            f"/api/recipes/{URLsTests.recipe.pk}/shopping_cart/": {},

            f"/api/recipes/{URLsTests.recipe.pk}/favorite/": {},

            "/api/users/subscriptions/": {},

            "/api/ingredients/": {
                get: status.HTTP_200_OK,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                delete: status.HTTP_405_METHOD_NOT_ALLOWED,
                post: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED},

            f"/api/ingredients/{URLsTests.ingredient.pk}/": {
                get: status.HTTP_200_OK,
                patch: status.HTTP_405_METHOD_NOT_ALLOWED,
                delete: status.HTTP_405_METHOD_NOT_ALLOWED,
                post: status.HTTP_405_METHOD_NOT_ALLOWED,
                put: status.HTTP_405_METHOD_NOT_ALLOWED},
        }

        for url, methods_dict in urls.items():
            for http_method in all_check_methods:
                with self.subTest(url=url, method=http_method.__name__):
                    expected_status = methods_dict.get(
                        http_method, status.HTTP_401_UNAUTHORIZED)
                    response: HttpResponse = http_method(url)
                    self.assertEquals(response.status_code, expected_status)
