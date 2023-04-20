from django.contrib import admin
from users.models import User, Subscribe
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin


class UserAdmin(DefaultUserAdmin):
    list_filter = ['email', 'username']


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe)
