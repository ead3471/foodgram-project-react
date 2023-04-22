from django.contrib import admin
from users.models import User, Subscribe
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.admin import register


@register(User)
class UserAdmin(DefaultUserAdmin):
    list_filter = ['email', 'username']
    list_display = ['is_active', 'username',
                    'first_name', 'last_name', 'email']


@register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscribe']
    list_filter = ['user', 'subscribe']
