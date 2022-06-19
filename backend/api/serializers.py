from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            Shopping, Tag)
from users.models import Follow

from .fields import ImageConversion

User = get_user_model()


class UserSerializer(UserCreateSerializer):
    """Сериализация для пользователей"""
    id = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password')
        qs = User.objects.all()  # почему, оно используется дважды
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
        if username.lower() == 'me':
            raise ValidationError('"me" is not valid username')
        return username


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Сериализация поля рецепт в при получении подписчиков и
    при добавлении в избранное"""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализация для списка подписчиков"""
    recipes = RecipeSmallSerializer(
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

    def to_representation(self, instance):
        representation = super(
            SubscribeSerializer, self).to_representation(instance)
        query = self.context.get('request').query_params
        if 'recipes_limit' in query:
            limit = int(query['recipes_limit'])
            if representation['recipes_count'] > limit:
                representation['recipes'] = representation['recipes'][:limit]
        return representation


class FollowSerializer(serializers.ModelSerializer):
    """Сериализация при создании подписчиков"""
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


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализация для ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализация поля игредиентов при получении рецепта(ов)"""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализация для тегов"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializerGet(serializers.ModelSerializer):
    """Сериализация получения рецепта(ов)"""
    tags = TagSerializer(many=True)
    ingredients = IngredientAmountSerializer(
        many=True, source='recipe_to_ingredient')
    author = UserSerializer(required=False, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = ImageConversion()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        favorite = Favorite.objects.filter(user=user.id, recipe=obj.id)
        return favorite.exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        shopping = Shopping.objects.filter(user=user.id, recipe=obj.id)
        return shopping.exists()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализация для создания и обновления рецепта"""
    author = UserSerializer(required=False, read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True, source='recipe_to_ingredient')
    image = ImageConversion()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def validate(self, data):
        tags = data['tags']
        tags_list = []
        for tags_item in tags:
            if tags_item in tags_list:
                raise serializers.ValidationError(
                    'Тэги должны быть уникальными')
            tags_list.append(tags_item)
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хотя бы один ингридиент для рецепта'})
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными')
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) <= 0:
                raise serializers.ValidationError({
                    'ingredients': ('Количества ингредиента должно быть > 0')})
        return data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        favorite = Favorite.objects.filter(user=user.id, recipe=obj.id)
        if favorite.exists():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        shopping = Shopping.objects.filter(user=user.id, recipe=obj.id)
        return shopping.exists()

    def crate_ingredients(self, recipe, ingredients):
        IngredientAmount.objects.bulk_create([
            IngredientAmount(
                recipe=recipe,
                ingredient_id=ingredient['ingredient']['id'],
                amount=ingredient['amount'],
            ) for ingredient in ingredients
        ])

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_to_ingredient', {})
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.crate_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        IngredientAmount.objects.filter(recipe=instance).delete()
        self.crate_ingredients(
            recipe=instance,
            ingredients=validated_data.pop('recipe_to_ingredient')
        )
        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        representation = super(
            RecipeSerializer, self).to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags, many=True, required=False).data
        return representation


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализация при добавления рецепта в избранные"""
    class Meta:
        fields = ('user', 'recipe')
        model = Favorite

    def to_representation(self, instance):
        request = self.context.get('request')
        recipe = get_object_or_404(Recipe, id=instance.recipe_id)
        representation = RecipeSmallSerializer(
            recipe, context={'request': request})
        return representation.data


class ShoppingSerializer(serializers.ModelSerializer):
    """Сериализация при добавления рецепта в избранные"""
    class Meta:
        fields = ('user', 'recipe')
        model = Shopping

    def to_representation(self, instance):
        request = self.context.get('request')
        recipe = get_object_or_404(Recipe, id=instance.recipe_id)
        representation = RecipeSmallSerializer(
            recipe, context={'request': request})
        return representation.data
