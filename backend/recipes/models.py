from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Tag storage model."""

    name = models.CharField(
        'Tag name', max_length=16, db_index=True, unique=True)
    color = models.CharField(verbose_name='Color', max_length=16, unique=True)
    slug = models.SlugField('Short name', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient storage model."""

    name = models.CharField(
        'Ingredient name', max_length=200, db_index=True)
    measurement_unit = models.CharField('Unit of measure', max_length=50)

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe storage model."""

    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='List of ingredients',
        through='IngredientAmount')
    tags = models.ManyToManyField(Tag, verbose_name='List of tag id')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipe')
    image = models.ImageField(
        upload_to='api/images/recipes/', verbose_name='Picture')
    name = models.CharField('Название рецепта', max_length=200, db_index=True)
    text = models.TextField('Description')
    cooking_time = models.PositiveSmallIntegerField(
        'Cooking time (in minutes)',
        validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Model for storing ingredient data in a recipe."""

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ingredient',
        related_name='ingredient_to_recipe')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Recipe',
        related_name='recipe_to_ingredient')
    amount = models.PositiveSmallIntegerField(
        'Quantity', default=1, validators=[MinValueValidator(1), ])

    class Meta:
        verbose_name = 'Recipe ingredients'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique_ingredient')
        ]

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class Favorite(models.Model):
    """Model for storing favourite recipes."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owner')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorite_recipe')

    class Meta:
        verbose_name = 'Favorites'
        verbose_name_plural = 'Favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favrecipe')
        ]

    def __str__(self):
        return f'{self.user.username} on {self.recipe.name}'


class Shopping(models.Model):
    """Model for storing recipes in the shopping list."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='byer')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_recipe')

    class Meta:
        verbose_name = 'Shopping list'
        verbose_name_plural = 'Shopping lists'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoprecipe')
        ]

    def __str__(self):
        return f'{self.user.username} on {self.recipe.name}'
