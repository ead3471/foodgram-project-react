import shutil
import tempfile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient as Client
from django.contrib.auth import get_user_model
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.conf import settings
from .utils import create_image

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class URLsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author_1 = User.objects.create(email='some@some.com',
                                           username='some_name_1')
        cls.user_1 = User.objects.create(email='some1@some1.com',
                                         username='some_name_2')

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

        cls.recipe.tag.set((cls.tag,))

        cls.recipe_ingredient = RecipeIngredient(
            ingredient=cls.ingredient,
            amount=2,
            recipe=cls.recipe
        )

    def setUp(self) -> None:
        super().setUp()
        self.anon_client = Client()

        self.user_1_client = Client()
        user_1_token = Token.objects.create(user=URLsTests.user_1)
        self.user_1_client.credentials(
            HTTP_AUTHORIZATION='Token ' + user_1_token.key)

        self.author_client = Client()
        author_token = Token.objects.create(user=URLsTests.author_1)
        self.author_client.credentials(
            HTTP_AUTHORIZATION='Token ' + author_token.key)

    def test_ingredients_view(self):
        pass
