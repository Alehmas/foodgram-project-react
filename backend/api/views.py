from django.contrib.auth import get_user_model
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserViewSet
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from recipes.models import Favorite, Ingredient, Recipe, Shopping, Tag
from users.models import Follow

from .filters import RecipeFilter
from .permissions import IsAdminOrAuthor, IsAdminOrAuthorOrReadOnly
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeSerializer,
                          RecipeSerializerGet, ShoppingSerializer,
                          SubscribeSerializer, TagSerializer)

User = get_user_model()


class UserViewSet(DjoserViewSet):
    """Вывод списка,создание и др для пользователей при работе с Djoser +
    создание, удаление и вывод списка подписчиков"""
    queryset = User.objects.all()
    permission_classes = [IsAdminOrAuthorOrReadOnly]
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('id',)
    ordering = ('id',)

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
                    'errors': 'Данная подписка отсутвует'
                    }, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=[permissions.IsAuthenticated, IsAdminOrAuthor])
    def subscriptions(self, request):
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
    """Вывод списка игредиентов или одного ингредиента"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вывод списка тегов или одного тега"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Отображение рецепта(ов) при Get, Post, Patch, Del"""
    queryset = Recipe.objects.all()
    permission_classes = [IsAdminOrAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,
                       filters.OrderingFilter,
                       filters.SearchFilter)
    filterset_class = RecipeFilter
    search_fields = ('^ingredients_name',)
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
        if request.method == 'POST':
            already = model.objects.filter(
                user=self.request.user.id, recipe=int(self.kwargs['pk']))
            if already.exists():
                return Response({
                    'errors': f'Рецепт уже в {err_text}'
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
                    'errors': f'Рецепт отсутствует в {err_text}'
                    }, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.add_favorite_shopping(
            request, Favorite, FavoriteSerializer, 'избранном')

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.add_favorite_shopping(
            request, Shopping, ShoppingSerializer, 'в списке покупок')

    @action(detail=False,
            permission_classes=[permissions.IsAuthenticated, IsAdminOrAuthor])
    def download_shopping_cart(self, request):
        data_ingredient = Recipe.objects.filter(
            shopping_recipe__user=self.request.user).values(
                ingredient_name=F(
                    'recipe_to_ingredient__ingredient__name'
                ),
                ingredient_measurement_unit=F(
                    'recipe_to_ingredient__ingredient__measurement_unit'
                ),
                amount=F(
                    'recipe_to_ingredient__amount'
                )
            )
        list_ingredient = list()
        for ingredient in data_ingredient:
            for i in list_ingredient:
                if ingredient['ingredient_name'] == i['ingredient_name']:
                    i['amount'] += ingredient['amount']
            if (ingredient['ingredient_name'] not in
                    [x['ingredient_name'] for x in list_ingredient]):
                list_ingredient.append(ingredient)
        shopping_cart = list()
        for ing in list_ingredient:
            name = ing['ingredient_name']
            measure = ing['ingredient_measurement_unit']
            amount = ing['amount']
            shopping_cart.append(f"{name.capitalize()} ({measure}) - {amount}")
            response = Response(shopping_cart,  content_type='text/plain')
        return response
