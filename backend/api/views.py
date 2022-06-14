from multiprocessing import context
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserViewSet
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from recipes.models import Ingredient, Recipe, Tag
from users.models import Follow
from .serializers import (
    IngredientSerializer, FollowSerializer, RecipeSerializer,
    RecipeSerializerGet, SubscribeSerializer, TagSerializer, UserSerializer)


User = get_user_model()


class UserViewSet(DjoserViewSet):
    """Вывод списка,создание и др для пользователей при работе с Djoser + 
    создание, удаление и вывод списка подписчиков"""
    queryset = User.objects.all()

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
            serializer = FollowSerializer(data=data, context={'request': request})
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

    @action(detail=False)
    def subscriptions(self, request):
        sub_user = User.objects.filter(following__user=self.request.user)
        serializer = SubscribeSerializer(
            sub_user, context={'request': request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Вывод списка игредиентов или одного ингредиента"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вывод списка тегов или одного тега"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Отображение рецепта(ов) при Get, Post, Patch, Del"""
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializerGet
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    """
    def get_serializer_context(self):
        context = super(RecipeViewSet, self).get_serializer_context()
        context.update(
            {'request': self.request})
        return context
    """
    
    """
    class SubscribeViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SubscribeSerializer
        return FollowSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        if request.method == 'POST':
            data = request.data.copy()
            following = int(self.kwargs['pk'])
            user = self.request.user.id
            data.update({'following': following, 'user': user})
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            follow = Follow.objects.filter(
                user=self.request.user.id, following=int(self.kwargs['pk']))
            if follow.exists():
                follow.delete()
            else:
                raise ValidationError('Данная подписка отсутвует')
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_serializer_context(self):
        context = super(SubscribeViewSet, self).get_serializer_context()
        context.update(
            {'request': self.request})
        return context
    
    
    @action(detail=True, methods=['delete'], url_path='subscribe')
    def destroy(self, request, *args, **kwargs):
        # following = get_object_or_404(User, id=)
        follow = Follow.objects.filter(
            user=self.request.user.id, following=int(kwargs['user_id']))
        if follow.exist():
            follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_serializer_context(self):
        context = super(SubscribeViewSet, self).get_serializer_context()
        following = int(self.kwargs['user_id'])
        user = self.request.user.id
        #follow = User.objects.filter(id=following)[0]
        context.update(
            {'following': following, 'user': user})
        return context
    
    def perform_create(self, serializer):
        user = self.request.user.id
        following = int(self.kwargs['user_id'])
        if user == following:
            raise ValidationError('Подписаться на самого себя нельзя')
        #else:
        #    Follow.objects.get_or_create(user=user, following=following)
        #follow = User.objects.filter(id=following)
        serializer.save()
    
    def perform_create(self, serializer):
        user = self.request.user.id
        following = int(self.kwargs['user_id'])
        if user == following:
            raise ValidationError('Подписаться на самого себя нельзя')
        Follow.objects.get_or_create(user=user, following=following)
        serializer.save()
    


    class FollowViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    # permission_classes = (permissions.IsAuthenticated,)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('following__username',)

    def get_queryset(self):
        return Follow.objects.filter(user__following=self.request.user)

    def create(self, request, **kwargs):
        data = request.data.copy()
        # following = get_object_or_404(User, id=int(kwargs['user_id']))
        data.update({'following': int(kwargs['user_id']), 'user': self.request.user.id})
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, **kwargs):
        following = get_object_or_404(User, id=int(kwargs['user_id']))
        follow = Follow.objects.filter(user=self.request.user, following=following)
        if follow.exist():
            follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    """

