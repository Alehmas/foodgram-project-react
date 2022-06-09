import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag

User = get_user_model()


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
        print(value)
        return value.url

    def to_internal_value(self, data):
        try:
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = "image." + ext
            data = ContentFile(base64.b64decode(imgstr), name = file_name)
        except ValueError:
            raise serializers.ValidationError(
                'Картинка должна быть кодирована в base64'
            )
        print(settings.MEDIA_ROOT)
        return data


class RecipeSerializerGet(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientAmountSerializer(
        many=True, source='recipe_to_ingredient')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(
        many=True, source='recipe_to_ingredient')
    image = ImageConversion()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')

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


class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')
        qs = User.objects.all()
        extra_kwargs = {
            'username': {
                'validators': [
                    UniqueValidator(
                        queryset=qs
                    )
                ]
            },
            'email': {
                'validators': [
                    UniqueValidator(
                        queryset=qs
                    )
                ]
            }
        }

    def validate_username(self, username):
        if username == 'me':
            raise ValidationError('"me" is not valid username')
        return username


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id','username', 'first_name',
                  'last_name')


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id','username', 'first_name',
                  'last_name')


class TokenSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(allow_blank=False)

    class Meta:
        model = User
        fields = ('username', 'email')