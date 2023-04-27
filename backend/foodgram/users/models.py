from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='email',
        help_text='Set user email'
    )

    username = models.CharField(
        verbose_name='Unique username',
        help_text='Set user name please',
        max_length=150,
        unique=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='subscribings')  # подписки
    subscribe = models.ForeignKey(User,
                                  on_delete=models.CASCADE,
                                  related_name='subscribers')  # подписчики

    def __str__(self):
        return (f"{self.user.username}({self.user.pk})->"
                f"{self.subscribe.username}({self.subscribe.pk})")
