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

    #def __str__(self):
    #    return self.id


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента', max_length=200, db_index=True)
    measurement_unit = models.CharField('Единица измерения', max_length=50)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    #def __str__(self):
    #    return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='ингридиенты', through='IngredientRecipe')
    tags = models.ManyToManyField(Tag, verbose_name='Тэг')
    name = models.CharField('Название рецепта', max_length=200, db_index=True)
    text = models.TextField('Текст')
    cooking_time = models.PositiveSmallIntegerField(
        'Время готовки',
        validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    #def __str__(self):
    #    return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredient_to_recipe')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_to_ingredient')
    amount = models.PositiveSmallIntegerField(
        'Количество', validators=[MinValueValidator(1)])
    
    #def __str__(self):
    #    return f'{self.ingredient} {self.amount}'

