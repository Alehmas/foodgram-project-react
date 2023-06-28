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
    """Serialization for users."""

    id = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password')
        extra_kwargs = {
            'username': {
                'validators': [
                    UniqueValidator(
                        queryset=User.objects.all()
                    )
                ]
            },
            'email': {
                'validators': [
                    UniqueValidator(
                        queryset=User.objects.all()
                    )
                ]
            }
        }

    def get_is_subscribed(self, obj):
        """Return the subscription status."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(
                user=user.id, following=obj.id).exists()
        return False

    def validate_username(self, username):
        """Forbids using the 'me' as a username."""
        if username.lower() == 'me':
            raise ValidationError('"me" is not valid username')
        return username


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Serialization of the recipe field.

    - when getting subscribers
    - when added to favorites.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Serialization for list of subscribers."""

    recipes = RecipeSmallSerializer(
        many=True, read_only=True, source='recipe')
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        """Return the number of recipes."""
        return obj.recipe.count()

    def get_is_subscribed(self, obj):
        """Return the subscription status."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(
                user=user.id, following=obj.id).exists()
        return False

    def to_representation(self, instance):
        """Show the number of subscriptions according to the limit."""
        representation = super(
            SubscribeSerializer, self).to_representation(instance)
        query = self.context.get('request').query_params
        if 'recipes_limit' in query:
            limit = int(query['recipes_limit'])
            if representation['recipes_count'] > limit:
                representation['recipes'] = representation['recipes'][:limit]
        return representation


class FollowSerializer(serializers.ModelSerializer):
    """Serialize the creation of subscriptions."""

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
        """Will restrict subscription creation to itself."""
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Подписка на себя невозможна!')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Serialization for ingredients."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Serialize the ingredients field when getting the recipe(s)."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Serialization for tags."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializerGet(serializers.ModelSerializer):
    """Serialization of receipt of recipe(s)."""

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
        """Show the recipe has been added to favorites or not."""
        user = self.context.get('request').user
        favorite = Favorite.objects.filter(user=user.id, recipe=obj.id)
        return favorite.exists()

    def get_is_in_shopping_cart(self, obj):
        """Show the recipe has been added to the shopping list or not."""
        user = self.context.get('request').user
        shopping = Shopping.objects.filter(user=user.id, recipe=obj.id)
        return shopping.exists()


class RecipeSerializer(serializers.ModelSerializer):
    """Serialize to create and update recipe."""

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
        """Check recipe creation or update data.

        Are the ingredients listed.
        Are the tags and ingredients unique.
        """
        tags = data['tags']
        tags_list = []
        for tags_item in tags:
            if tags_item in tags_list:
                raise serializers.ValidationError(
                    'Тэги должны быть уникальными')
            tags_list.append(tags_item)
        ingredients = data['recipe_to_ingredient']
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент для рецепта'})
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_item['ingredient']['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными')
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) <= 0:
                raise serializers.ValidationError({
                    'ingredients': ('Количества ингредиента должно быть > 0')})
        return data

    def get_is_favorited(self, obj):
        """Show the recipe has been added to favorites or not."""
        user = self.context.get('request').user
        favorite = Favorite.objects.filter(user=user.id, recipe=obj.id)
        return favorite.exists()

    def get_is_in_shopping_cart(self, obj):
        """Show the recipe has been added to the shopping list or not."""
        user = self.context.get('request').user
        shopping = Shopping.objects.filter(user=user.id, recipe=obj.id)
        return shopping.exists()

    def create_ingredients(self, recipe, ingredients):
        """Create a new ingredient."""
        IngredientAmount.objects.bulk_create([
            IngredientAmount(
                recipe=recipe,
                ingredient_id=ingredient['ingredient']['id'],
                amount=ingredient['amount'],
            ) for ingredient in ingredients
        ])

    def create(self, validated_data):
        """Create a new recipe."""
        ingredients = validated_data.pop('recipe_to_ingredient', {})
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        IngredientAmount.objects.filter(recipe=instance).delete()
        self.create_ingredients(
            recipe=instance,
            ingredients=validated_data.pop('recipe_to_ingredient')
        )
        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        """Show a recipe with a list of tags."""
        representation = super(
            RecipeSerializer, self).to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags, many=True, required=False).data
        return representation


class FavoriteSerializer(serializers.ModelSerializer):
    """Serialization when adding/deleting a recipe to favorites."""

    class Meta:
        fields = ('user', 'recipe')
        model = Favorite

    def to_representation(self, instance):
        """Show the recipe after adding/deleting to favorites."""
        request = self.context.get('request')
        recipe = get_object_or_404(Recipe, id=instance.recipe_id)
        representation = RecipeSmallSerializer(
            recipe, context={'request': request})
        return representation.data


class ShoppingSerializer(serializers.ModelSerializer):
    """Serialization when adding a recipe to the shopping list."""

    class Meta:
        fields = ('user', 'recipe')
        model = Shopping

    def to_representation(self, instance):
        """Show the recipe after adding/deleting to the shopping list."""
        request = self.context.get('request')
        recipe = get_object_or_404(Recipe, id=instance.recipe_id)
        representation = RecipeSmallSerializer(
            recipe, context={'request': request})
        return representation.data
