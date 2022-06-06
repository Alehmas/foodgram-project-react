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


class ImageConversion(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            decode = BytesIO(base64.b64decode(data))
            image = Image.open(decode)
        except ValueError:
            raise serializers.ValidationError(
                'Картинка должна быть кодирована в base64'
            )
        return image


class RecipeSerializerGet(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    image = ImageConversion()
    ingredients = IngredientAmountSerializer(
        many=True, source='recipe_to_ingredient')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(
        many=True, source='recipe_to_ingredient')
    
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'name', 'text', 'cooking_time')

    def crate_ingredients(self, recipe, ingredients):
        for ingredient in ingredients:
            amount = ingredient.pop('amount')
            id = ingredient.pop('id')
            current_ingredient = get_object_or_404(Ingredient, id=id)
            IngredientAmount.objects.create(
                ingredient=current_ingredient, recipe=recipe, amount=amount
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_to_ingredient', {})
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.crate_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe
    
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_to_ingredient', {})
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.filter(id=instance.id).delete()
        recipe = Recipe.objects.create(id=instance.id, **validated_data)
        self.crate_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe
    
    def to_representation(self, instance):
        representation = super(
            RecipeSerializer, self).to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags, many=True, required=False).data
        return representation
