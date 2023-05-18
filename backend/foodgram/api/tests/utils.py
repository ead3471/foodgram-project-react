from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
import base64
from django.test import TestCase
from recipes.models import Recipe
import jsonschema

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
    """Creates Token for given client and set this token as the
    credentials of given APIClient

    Parameters
    ----------
    client : APIClient
        APIClient instance
    user : User
        user instance

    Returns
    -------
    Token
        new token for the given user instance
    """
    token = Token.objects.create(user=user)
    client.credentials(HTTP_AUTHORIZATION="Token " + token.key)


def test_json_schema(test: TestCase, schema, tested_json):
    """Tests given in @tested_json dict by given in @schema json schema

    Parameters
    ----------
    test : TestCase
        TestCase Instance
    schema : _type_
        JSON validation schema
    tested_json : _type_
        data for validation
    """
    try:
        jsonschema.validate(
            tested_json,
            schema,
        )
    except jsonschema.exceptions.ValidationError as e:
        test.fail(f"Response data validation failed. Error details:{e}")


def test_recipe_content(
    test: TestCase, expected_data: dict, recipe_object: Recipe
):
    """Checks the fields of the given recipe_object for equivalence
    to the given expected_data

    Parameters
    ----------
    test : TestCase
        TestCase object
    expected_data : dict
        dict with expected fields values. Must be in this form:\n
        recipe_data = {\n
            "name": "new_recipe_name",\n
            "text": "new_some_text",\n
            "cooking_time": 4,\n
            "tags": [\n
                <id>,\n
                ...\n
            ],\n
            "ingredients": [\n
                {"id": <id>, "amount": <amount>},\n
                ...\n
            ],\n
            "image": <ImageObject>,\n
        }\n

    recipe_object : Recipe
        Recipe object
    """
    test.assertEqual(recipe_object.name, expected_data["name"])
    test.assertEqual(recipe_object.text, expected_data["text"])
    test.assertEqual(recipe_object.cooking_time, expected_data["cooking_time"])
    test.assertEqual(
        list(recipe_object.tag.all().values_list("id", flat=True)),
        expected_data["tags"],
    )
    test.assertEqual(
        [
            {
                "id": recipe_ingredient.ingredient.id,
                "amount": recipe_ingredient.amount,
            }
            for recipe_ingredient in recipe_object.ingredients.all()
        ],
        expected_data["ingredients"],
    )
