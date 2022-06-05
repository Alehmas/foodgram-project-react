from rest_framework import serializers
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from django.shortcuts import get_object_or_404


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientRecipe
        fields = ('__all__')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)
    
    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializerGet(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True, source='recipe_to_ingredient')

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name', 'text', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(many=True, source='recipe_to_ingredient')
    tags = serializers.SlugRelatedField(
        many=True, slug_field='id',
        queryset=Tag.objects.all()
    )
    
    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'name', 'text', 'cooking_time')
        depth = 1

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_to_ingredient', {})
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            amount = ingredient.pop('amount')
            id = ingredient.pop('id')
            current_ingredient = get_object_or_404(Ingredient, id=id)
            IngredientRecipe.objects.create(
                ingredient=current_ingredient, recipe=recipe, amount=amount
            )
        recipe.tags.set(tags)
        return recipe
