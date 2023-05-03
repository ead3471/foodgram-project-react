from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from users import Setup


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=Setup.EMAIL_MAX_LENGTH,
        verbose_name='email',
        help_text='Set user email'
    )

    username = models.CharField(
        verbose_name='Unique username',
        help_text='Set user name please',
        max_length=Setup.EMAIL_MAX_LENGTH,
        unique=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

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

    def clean(self) -> None:
        if self.user == self.subscribe:
            raise ValidationError("The user cannot subscribe to himself!")

        return super().clean()

    class Meta:
        verbose_name = 'Subscribe'
        verbose_name_plural = 'Subscribes'
        unique_together = ('user', 'subscribe')

    def __str__(self):
        return (f"{self.user.username}({self.user.pk})->"
                f"{self.subscribe.username}({self.subscribe.pk})")
