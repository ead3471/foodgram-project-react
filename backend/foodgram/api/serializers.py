from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import Subscribe
from django.shortcuts import get_object_or_404

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
