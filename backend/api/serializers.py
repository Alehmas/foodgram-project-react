from rest_framework import serializers
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from django.shortcuts import get_object_or_404


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')
  
    def to_representation(self, instance):
        return {'id': instance.ingredient_id,
                'name': instance.ingredient.name,
                'measurement_unit': instance.ingredient.measurement_unit,
                'amount': instance.amount}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializerGet(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField()
    tags = TagSerializer(many=True)
    ingredients = IngredientAmountSerializer(
        many=True, source='recipe_to_ingredient')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'name', 'text', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(
        many=True, source='recipe_to_ingredient')
    
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'name', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_to_ingredient', {})
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            amount = ingredient.pop('amount')
            id = ingredient.pop('id')
            current_ingredient = get_object_or_404(Ingredient, id=id)
            IngredientAmount.objects.create(
                ingredient=current_ingredient, recipe=recipe, amount=amount
            )
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        representation = super(
            RecipeSerializer, self).to_representation(instance)
        #print(representation.__dir__)
        # representation['id'] = instance.id
        representation['tags'] = TagSerializer(
            instance.tags, many=True, required=False).data
        return representation
