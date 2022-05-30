from django.core.validators import MinValueValidator
from django.db import models


class Tag(models.Model):
    name = models.CharField(
        'Название тега', max_length=16, db_index=True, unique=True)
    color = models.CharField(verbose_name='Цвет', max_length=16, unique=True)
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
    amount = models.PositiveSmallIntegerField(
        'Количество', validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.id


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='ингридиенты')
    tags = models.ManyToManyField(Tag, verbose_name='Тэг')
    name = models.CharField('Название рецепта', max_length=200, db_index=True)
    text = models.TextField('Текст')
    cooking_time = models.PositiveSmallIntegerField(
        'Время готовки',
        validators=[MinValueValidator(1)])
