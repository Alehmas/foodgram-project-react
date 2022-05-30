from rest_framework import serializers
from recipes.models import Ingredient, Recipe, Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializerGet(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name', 'text', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    # ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name', 'text', 'cooking_time')