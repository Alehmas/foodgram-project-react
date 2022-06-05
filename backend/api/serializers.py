from re import I
from rest_framework import serializers
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from django.shortcuts import get_object_or_404


class IngredientSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField(source='ingredient_to_recipe')

    def get_amount(self, obj):
        print(dir(obj.ingredient_to_recipe)) # остановился здесь
        amount = obj.id
        return amount

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)
    amount = serializers.IntegerField()
    
    def to_representation(self, instance):
        return {'id': instance.ingredient_id,
                'name': instance.ingredient.name,
                'measurement_unit': instance.ingredient.measurement_unit,
                'amount': instance.amount}

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializerGet(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(
        many=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name', 'text', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(
        many=True, source='recipe_to_ingredient')
    tags = serializers.SlugRelatedField(
        many=True, slug_field='id',
        queryset=Tag.objects.all()
    )
    
    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name', 'text', 'cooking_time')

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
