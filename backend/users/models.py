from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'user'), (ADMIN, 'admin')
    )
    email = models.EmailField('Адрес электронной почты', max_length=254)
    username = models.CharField(
        'Уникальный юзернейм', max_length=150, unique=True)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    password = models.CharField('Пароль', max_length=150)
    role = models.CharField(
        max_length=30, choices=ROLE_CHOICES, default=USER
    )

    def save(self, *args, **kwargs):
        if self.role == self.ADMIN:
            self.is_superuser = True
        super().save(*args, **kwargs)


