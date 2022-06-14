import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from django.conf import settings
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from users.models import Follow

User = get_user_model()


class UserSerializer(UserCreateSerializer):
    """Сериализация для пользователей"""
    id = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password')
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
    
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(
                user=user.id, following=obj.id).exists()
        return False

    def validate_username(self, username):
        if username == 'me':
            raise ValidationError('"me" is not valid username')
        return username


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    """Сериализация поля рецепт в при получении подписчиков"""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализация для списка подписчиков"""
    recipes = RecipeSubscribeSerializer(
        many=True, read_only=True, source='recipe')
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipe.count()
    
    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(
                user=user.id, following=obj.id).exists()
        return False


class FollowSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = ('user', 'following')
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following']
            )
        ]

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Подписка на себя невозможна!')
        return data
    
    def to_representation(self, instance):
        follow = get_object_or_404(User, id=instance.following_id)
        representation = SubscribeSerializer(follow).data
        return representation
    

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализация для ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализация поля игредиентов при получении рецепта(ов)"""
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
    """Сериализация для тегов"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class ImageConversion(serializers.Field):
    """Сериализация для поля изображения в рецепте"""
    def to_representation(self, value):
        return value.url

    def to_internal_value(self, data):
        try:
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = "image." + ext
            data = ContentFile(base64.b64decode(imgstr), name=file_name)
        except ValueError:
            raise serializers.ValidationError(
                'Картинка должна быть кодирована в base64'
            )
        return data


class RecipeSerializerGet(serializers.ModelSerializer):
    """Сериализация получения рецепта(ов)"""
    tags = TagSerializer(many=True)
    ingredients = IngredientAmountSerializer(
        many=True, source='recipe_to_ingredient')
    author = UserSerializer(required=False, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализация для создания и обновления рецепта"""
    author = UserSerializer(required=False, read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True, source='recipe_to_ingredient')
    image = ImageConversion()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
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

