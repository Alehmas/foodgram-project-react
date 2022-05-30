from rest_framework import filters, permissions, status, viewsets
from recipes.models import Ingredient, Recipe, Tag
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeSerializerGet, TagSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializerGet
        return RecipeSerializer
