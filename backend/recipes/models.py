from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'Название тега', max_length=16, db_index=True, unique=True)
    color = models.CharField(verbose_name='Цвет', max_length=16, unique=True)
    slug = models.SlugField('Короткое название', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента', max_length=200, db_index=True)
    measurement_unit = models.CharField('Единица измерения', max_length=50)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Список ингредиентов',
        through='IngredientAmount')
    tags = models.ManyToManyField(Tag, verbose_name='Список id тегов')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipe')
    image = models.ImageField(
        upload_to='api/images/recipes/', verbose_name='Картинка')
    name = models.CharField('Название', max_length=200, db_index=True)
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент',
        related_name='ingredient_to_recipe')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
        related_name='recipe_to_ingredient')
    amount = models.PositiveSmallIntegerField(
        'Количество', default=1, validators=[MinValueValidator(1), ])

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique_ingredient')
        ]

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owner')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorite_recipe')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favrecipe')
        ]

    def __str__(self):
        return f'{self.user.username} on {self.recipe.name}'


class Shopping(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='byer')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_recipe')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoprecipe')
        ]

    def __str__(self):
        return f'{self.user.username} on {self.recipe.name}'
