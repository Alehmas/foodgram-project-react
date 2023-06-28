from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    """User storage model."""

    email = models.EmailField(
        'E-mail address', max_length=254, unique=True)
    username = models.CharField(
        'Unique username', max_length=150, unique=True)
    first_name = models.CharField('Name', max_length=150)
    last_name = models.CharField('Surname', max_length=150)
    password = models.CharField('Password', max_length=150)
    is_subscribed = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Model for storing user subscriptions."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_following')
        ]

    def __str__(self):
        return f'{self.user.username} on {self.following.username}'

    def clean(self):
        if self.user == self.following:
            raise ValidationError('You can`t subscribe to yourself')
