from django.contrib import admin
from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from users.models import Subscribe, User


@register(User)
class UserAdmin(DefaultUserAdmin):
    list_filter = ['email', 'username']
    list_display = ['is_active', 'username',
                    'first_name', 'last_name', 'email']


@register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscribe']
    list_filter = ['user', 'subscribe']
