from rest_framework import filters, permissions, status, viewsets
from recipes.models import Ingredient, Recipe, Tag
from .serializers import (IngredientSerializer, RecipeSerializer,
                          TagSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
