from django_filters import rest_framework as filters
from rest_framework import filters as filter

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    """Filter recipes."""

    author = filters.CharFilter(field_name='author_id')
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Filter recipes by favorites."""
        if self.request.user.is_authenticated:
            if value == 1:
                return queryset.filter(**{
                    'favorite_recipe__user': self.request.user})
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Filter recipes by shopping list."""
        if self.request.user.is_authenticated:
            if value == 1:
                return queryset.filter(**{
                    'shopping_recipe__user': self.request.user})
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']


class IngredientFilter(filter.SearchFilter):
    """Filter to search for ingredients."""

    search_param = 'name'
