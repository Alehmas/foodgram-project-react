from rest_framework import serializers
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientSerializerRecipe(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


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
    ingredients = IngredientSerializerRecipe(many=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name', 'text', 'cooking_time')
    
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        print(ingredients)
        print(type(validated_data))
        print(validated_data)
        recipe = Recipe.objects.set(**validated_data)
        for ingredient in ingredients:
            print(ingredient.id)
            current_ingredient, status = Ingredient.objects.get_or_create(**ingredient)
            IngredientRecipe.objects.create(
                ingredient=current_ingredient, recipe=recipe
            )
        return recipe
