from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.apps import apps
import base64
from django.test import TestCase

User = get_user_model()


def create_image() -> SimpleUploadedFile:
    small_gif = (
        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
        b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
        b"\x02\x4c\x01\x00\x3b"
    )
    return SimpleUploadedFile("small.gif", small_gif, content_type="image/gif")


def get_byte_64_image() -> str:
    image = create_image()
    return base64.b64encode(image.read()).decode()


def authorize_client_by_user(client: APIClient, user: User) -> Token:
    token = Token.objects.create(user=user)
    client.credentials(HTTP_AUTHORIZATION="Token " + token.key)


def auto_tear_down(cls):
    def dell_method(*args, **kwargs):
        print(f"in tear down for {cls}")
        all_models = apps.get_models()
        for model in all_models:
            model.objects.all().delete()

    cls.tearDown = dell_method
    return cls


def test_response_content(test: TestCase, response_data, required_fields):
    for field in required_fields:
        if isinstance(field, dict):
            main_field_name = list(field.keys())[0]
            with test.subTest(field=main_field_name):
                test.assertIn(
                    main_field_name,
                    response_data,
                )
            for sub_field in field[main_field_name]:
                with test.subTest(sub_field=sub_field):
                    for responce_element in response_data[main_field_name]:
                        test.assertIn(sub_field, responce_element)
        else:
            with test.subTest(field=field):
                test.assertIn(
                    field,
                    response_data,
                )
