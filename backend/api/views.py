from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserViewSet
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, Shopping, Tag
from users.models import Follow
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAdminOrAuthor, IsAdminOrAuthorOrReadOnly
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeSerializer,
                          RecipeSerializerGet, ShoppingSerializer,
                          SubscribeSerializer, TagSerializer)

User = get_user_model()


class UserViewSet(DjoserViewSet):
    """Get, create user(s) or get, create or delete subscription(s).

    list:
    Get a list of all users.
    Get a list of user's subscriptions.

    create:
    Register user.
    Change users password.
    Create a subscription to another user.

    retrieve:
    Get a user by id.
    Get your account information.

    destroy:
    Remove a subscription to another user.
    """

    queryset = User.objects.all()
    permission_classes = [IsAdminOrAuthorOrReadOnly]
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('id',)
    ordering = ('id',)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        """Create or delete a subscription to another user."""
        if request.method == 'POST':
            already_follow = Follow.objects.filter(
                user=self.request.user.id, following=int(self.kwargs['id']))
            if already_follow.exists():
                return Response({
                    'errors': 'You are already following this user'
                    }, status=status.HTTP_400_BAD_REQUEST)
            following = int(self.kwargs['id'])
            user = self.request.user.id
            serializer = FollowSerializer(
                data={'following': following, 'user': user},
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = SubscribeSerializer(
                serializer.instance.following, context={'request': request})
            return Response(response.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            follow = Follow.objects.filter(
                user=self.request.user.id, following=int(self.kwargs['id']))
            if follow.exists():
                follow.delete()
            else:
                return Response({
                    'errors': 'This subscription is missing'
                    }, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=[permissions.IsAuthenticated, IsAdminOrAuthor])
    def subscriptions(self, request):
        """Get the users that the current user is following."""
        sub_user = User.objects.filter(following__user=self.request.user)
        page = self.paginate_queryset(sub_user.order_by('id'))
        if page is not None:
            serializer = SubscribeSerializer(
                page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeSerializer(
            sub_user, context={'request': request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Displaying a list of ingredients or a single ingredient.

    list:
    Get a list of ingredients.

    retrieve:
    Get a ingredient by id.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientFilter,)
    filterset_class = RecipeFilter
    search_fields = ('^name',)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Displaying a list of tags or a single tag.

    list:
    Get a list of tags.

    retrieve:
    Get a tag by id.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Recipe(s) display on Get, Post, Patch, Del.

    list:
    Get a list of recipes.

    create:
    Create a recipe.

    retrieve:
    Get a recipe by id.

    partial_update:
    Patch a recipe.

    destroy:
    Remove a recipe by id.
    """

    queryset = Recipe.objects.all()
    permission_classes = [IsAdminOrAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,
                       filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering_fields = ('id',)
    ordering = ('-id',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializerGet
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def add_favorite_shopping(self, request, model, ser, err_text):
        """Add/remove a recipe to/from the favorites/shopping list."""
        if request.method == 'POST':
            already = model.objects.filter(
                user=self.request.user.id, recipe=int(self.kwargs['pk']))
            if already.exists():
                return Response({
                    'errors': f'Recipe already in {err_text}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            recipe = int(self.kwargs['pk'])
            user = self.request.user.id
            serializer = ser(
                data={'recipe': recipe, 'user': user},
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            already = model.objects.filter(
                user=self.request.user.id, recipe=int(self.kwargs['pk']))
            if already.exists():
                already.delete()
            else:
                return Response({
                    'errors': f'Recipe is not on the {err_text}'
                    }, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Add/remove a recipe to/from the favorites list."""
        return self.add_favorite_shopping(
            request, Favorite, FavoriteSerializer, 'избранном')

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Add/remove a recipe to/from the shopping list."""
        return self.add_favorite_shopping(
            request, Shopping, ShoppingSerializer, 'в списке покупок')

    @action(detail=False,
            permission_classes=[permissions.IsAuthenticated, IsAdminOrAuthor])
    def download_shopping_cart(self, request):
        """Return the shopping list."""
        data_ingredient = Recipe.objects.filter(
            shopping_recipe__user=self.request.user).values(
                ingredient_name=F(
                    'recipe_to_ingredient__ingredient__name'
                ),
                ingredient_measurement_unit=F(
                    'recipe_to_ingredient__ingredient__measurement_unit'
                )
            ).annotate(total_amount=Sum('recipe_to_ingredient__amount'))
        shopping_cart = list()
        for ing in data_ingredient:
            name = ing['ingredient_name']
            measure = ing['ingredient_measurement_unit']
            amount = ing['total_amount']
            shopping_cart.append(f"{name.capitalize()} ({measure}) - {amount}")
            response = Response(shopping_cart,  content_type='text/plain')
        return response
