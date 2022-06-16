from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from recipes.models import Favorite, Ingredient, Recipe, Shopping, Tag
from users.models import Follow

from .permissions import IsAuthor
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeSerializer,
                          RecipeSerializerGet, ShoppingSerializer,
                          SubscribeSerializer, TagSerializer)

User = get_user_model()


class UserViewSet(DjoserViewSet):
    """Вывод списка,создание и др для пользователей при работе с Djoser +
    создание, удаление и вывод списка подписчиков"""
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        if request.method == 'POST':
            already_follow = Follow.objects.filter(
                user=self.request.user.id, following=int(self.kwargs['id']))
            if already_follow.exists():
                return Response({
                    'errors': 'Вы уже подписаны на данного пользователя'
                    }, status=status.HTTP_400_BAD_REQUEST)
            data = request.data.copy()
            following = int(self.kwargs['id'])
            user = self.request.user.id
            data.update({'following': following, 'user': user})
            serializer = FollowSerializer(
                data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            follow = Follow.objects.filter(
                user=self.request.user.id, following=int(self.kwargs['id']))
            if follow.exists():
                follow.delete()
            else:
                return Response({
                    'errors': 'Данная подписка отсутвует'
                    }, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=[permissions.IsAuthenticated, IsAuthor])
    def subscriptions(self, request):
        sub_user = User.objects.filter(following__user=self.request.user)
        page = self.paginate_queryset(sub_user)
        if page is not None:
            serializer = serializer = SubscribeSerializer(
                page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeSerializer(
            page, context={'request': request}, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Вывод списка игредиентов или одного ингредиента"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вывод списка тегов или одного тега"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Отображение рецепта(ов) при Get, Post, Patch, Del"""
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializerGet
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super(RecipeViewSet, self).get_serializer_context()
        context.update(
            {'request': self.request})
        return context

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated, IsAuthor])
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            already_favorite = Favorite.objects.filter(
                user=self.request.user.id, recipe=int(self.kwargs['pk']))
            if already_favorite.exists():
                return Response({
                    'errors': 'Рецепт уже в избранном'
                    }, status=status.HTTP_400_BAD_REQUEST)
            data = request.data.copy()
            recipe = int(self.kwargs['pk'])
            user = self.request.user.id
            data.update({'recipe': recipe, 'user': user})
            serializer = FavoriteSerializer(
                data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(
                user=self.request.user.id, recipe=int(self.kwargs['pk']))
            if favorite.exists():
                favorite.delete()
            else:
                return Response({
                    'errors': 'Рецепт отсутствует в избранном'
                    }, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            already_cart = Shopping.objects.filter(
                user=self.request.user.id, recipe=int(self.kwargs['pk']))
            if already_cart.exists():
                return Response({
                    'errors': 'Рецепт уже в списке покупок'
                    }, status=status.HTTP_400_BAD_REQUEST)
            data = request.data.copy()
            recipe = int(self.kwargs['pk'])
            user = self.request.user.id
            data.update({'recipe': recipe, 'user': user})
            serializer = ShoppingSerializer(
                data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorite = Shopping.objects.filter(
                user=self.request.user.id, recipe=int(self.kwargs['pk']))
            if favorite.exists():
                favorite.delete()
            else:
                return Response({
                    'errors': 'Рецепт отсутствует в списке покупок'
                    }, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=[permissions.IsAuthenticated, IsAuthor])
    def download_shopping_cart(self, request):
        list_recipe = Recipe.objects.filter(
            shopping_recipe__user=self.request.user)
        serializer = RecipeSerializerGet(
            list_recipe, context={'request': request}, many=True)
        list_ingredient = list()
        for recipe in serializer.data:
            for ingredient in recipe['ingredients']:
                for i in list_ingredient:
                    if ingredient['id'] == i['id']:
                        i['amount'] += ingredient['amount']
                if ingredient['id'] not in [x['id'] for x in list_ingredient]:
                    list_ingredient.append(ingredient)
        shopping_cart = list()
        for ing in list_ingredient:
            name = ing['name'].capitalize()
            measure = ing['measurement_unit']
            amount = ing['amount']
            shopping_cart.append(f"{name} ({measure}) - {amount}")
            headers = {'Content-Type': 'application/txt',
                       'Content-Disposition': 'attachment; filename="foo.txt"'}
        return Response(shopping_cart, headers=headers, status=status.HTTP_200_OK)
