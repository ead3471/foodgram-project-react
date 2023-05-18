import pprint


def schema_to_strict(schema):
    if schema["type"] not in ["object", "array"]:
        return schema

    if schema["type"] == "array":
        schema["items"] = schema_to_strict(schema["items"])
        return schema

    for k, v in schema["properties"].items():
        schema["properties"][k] = schema_to_strict(v)

    schema["required"] = list(schema["properties"].keys())
    schema["additionalProperties"] = False
    return schema


USER_RESPONSE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "email": {"type": "string"},
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "is_subscribed": {"type": "boolean"},
    },
    "required": [],
}


TAG_RESPONCE_API_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "color": {"type": "string"},
        "slug": {"type": "string"},
    },
    "required": [],
}

TAG_ARRAY_RESPONSE_API_SCHEMA = {
    "type": "array",
    "items": TAG_RESPONCE_API_SCHEMA,
}

RECIPE_INGREDIENT_RESPONSE_API_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "measurement_unit": {"type": "string"},
        "amount": {"type": "integer"},
    },
}

RECIPE_INGREDIENT_ARRAY_RESPONSE_API_SCHEMA = {
    "type": "array",
    "items": RECIPE_INGREDIENT_RESPONSE_API_SCHEMA,
    "minItems": 1,
}


RECIPE_RESPONSE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "author": USER_RESPONSE_JSON_SCHEMA,
        "tags": TAG_ARRAY_RESPONSE_API_SCHEMA,
        "ingredients": RECIPE_INGREDIENT_ARRAY_RESPONSE_API_SCHEMA,
        "is_favorited": {"type": "boolean"},
        "is_in_shopping_cart": {"type": "boolean"},
        "name": {"type": "string"},
        "image": {"type": "string"},
        "text": {"type": "string"},
        "cooking_time": {"type": "integer"},
    },
}

RECIPES_PAGINATED_RESPONCE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "count": {"type": "integer"},
        "next": {"type": ["string", "null"]},
        "previous": {"type": ["string", "null"]},
        "results": {
            "type": "array",
            "items": RECIPE_RESPONSE_JSON_SCHEMA,
            "minItems": 1,
        },
    },
    "required": ["count", "results"],
}

schema_to_strict(RECIPE_RESPONSE_JSON_SCHEMA)
