from django.db import models
from django.core.validators import MinValueValidator


class Tag(models.Model):
    name = models.CharField(
        'Название тега', max_length=200, db_index=True, unique=True)
    color = models.TextField(verbose_name='ингридиенты', unique=True)  # редок
    slug = models.SlugField('Короткое название', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.id


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента', max_length=200, db_index=True)
    measurement_unit = models.CharField('Единица измерения', max_length=50)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.id


class Recipe(models.Model):
    ingredients = models.TextField(verbose_name='ингридиенты')  # редок
    tags = models.TextField(verbose_name='тэги')  # редок
    name = models.CharField('Название рецепта', max_length=200, db_index=True)
    text = models.TextField('Текст')
    cooking_time = models.PositiveSmallIntegerField(
        'Время готовки',
        validators=[MinValueValidator(1)])
