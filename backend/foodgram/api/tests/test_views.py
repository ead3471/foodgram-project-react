import shutil
import tempfile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient as Client
from django.contrib.auth import get_user_model
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from users.models import Subscribe
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.conf import settings
from .utils import create_image
from django.urls import reverse
from api.serializers import IngredientSerializer, TagSerializer, UserSerializer, SubscribeSerializer

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class TestIngredientsView(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.ingredient = Ingredient.objects.create(name='name',
                                                   measurement_unit='unit')

    def test_list(self):
        responce_data = self.client.get(reverse('ingredients-list')).data
        expected_data = IngredientSerializer(Ingredient.objects.all(),
                                             many=True).data
        self.assertEqual(responce_data, expected_data)

    def test_retrive(self):
        responce_data = self.client.get(
            reverse('ingredients-detail',
                    kwargs={'pk': TestIngredientsView.ingredient.pk})).data

        expected_data = IngredientSerializer(
            instance=TestIngredientsView.ingredient).data
        self.assertEqual(responce_data, expected_data)


class TestTagsView(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.tag = Tag.objects.create(name='name',
                                     slug='slug',
                                     color='#FFFFFF')

    def test_list(self):
        responce_data = self.client.get(reverse('tags-list')).data
        expected_data = TagSerializer(Tag.objects.all(),
                                      many=True).data
        self.assertEqual(responce_data, expected_data)

    def test_retrive(self):
        responce_data = self.client.get(
            reverse('tags-detail',
                    kwargs={'pk': TestTagsView.tag.pk})).data

        expected_data = TagSerializer(
            instance=TestTagsView.tag).data
        self.assertEqual(responce_data, expected_data)


class TestUsersView(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_1 = User.objects.create(
            email='some-email@email.com', username='some_name')

        user_1_token = Token.objects.create(user=cls.user_1)
        user_1_client = Client()
        user_1_client.credentials(
            HTTP_AUTHORIZATION='Token ' + user_1_token.key)
        cls.user_1_client = user_1_client

        cls.author_user = User.objects.create(
            email='some-author-email@email.com', username='author_name')

    def test_list(self):
        client = Client()
        responce_data = client.get(reverse('user-list')).data
        expected_data = UserSerializer(User.objects.all(),
                                       many=True).data
        self.assertEqual(responce_data, expected_data)

    def test_retrive(self):
        responce_data = self.client.get(
            reverse('user-detail',
                    kwargs={'id': TestUsersView.user_1.id})).data

        expected_data = UserSerializer(
            instance=TestUsersView.user_1).data
        self.assertEqual(responce_data, expected_data)

    def test_me(self):
        responce_data = TestUsersView.user_1_client.get(
            reverse('user-me')).data
        expected_data = UserSerializer(
            instance=TestUsersView.user_1).data
        self.assertEqual(responce_data, expected_data)

    def test_register_new_user(self):
        client = Client()
        reg_data = {'username': 'new_user',
                    'email': 'some@email.com',
                    'password': 'Aa123456789',
                    "first_name": "some_name",
                    "last_name": "some_name",

                    }
        client.post('/api/users/', data=reg_data)
        self.assertTrue(User.objects.filter(email=reg_data['email']).exists())


class TestSubscribeView(TestCase):
    def setUp(self) -> None:
        super().setUpClass()
        self.user_1 = User.objects.create(
            email='some-email@email.com', username='some_name')

        user_1_token = Token.objects.create(user=self.user_1)
        user_1_client = Client()
        user_1_client.credentials(
            HTTP_AUTHORIZATION='Token ' + user_1_token.key)
        self.user_1_client = user_1_client

        self.author_user = User.objects.create(
            email='some-author-email@email.com', username='author_name')

    def test_create_subscribe(self):
        resp = self.user_1_client.post(
            reverse(
                'subscribe',
                kwargs={'user_id': self.author_user.pk}))
        self.assertTrue(Subscribe.objects.filter(user=self.user_1,
                                                 subscribe=self.author_user).
                        exists())

    def test_remove_subscribe(self):
        subscribe = Subscribe.objects.create(user=self.user_1,
                                             subscribe=self.author_user)
        self.assertTrue(Subscribe.objects.filter(user=self.user_1,
                                                 subscribe=self.author_user).
                        exists())
        resp = self.user_1_client.delete(
            reverse(
                'subscribe',
                kwargs={'user_id': self.author_user.pk}))
        self.assertFalse(Subscribe.objects.filter(user=self.user_1,
                                                  subscribe=self.author_user).
                         exists())

    def test_subscriptions_list(self):
        resp = self.user_1_client.get(reverse('subscriptions'))
        expected_data = SubscribeSerializer(
            Subscribe.objects.filter(user=self.user_1,
                                     subscribe=self.author_user),
            many=True).data
        self.assertEqual(resp.data, expected_data)
