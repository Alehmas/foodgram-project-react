from django_filters import rest_framework as filters
from recipes.models import Recipe
from distutils.util import strtobool

BOOLEAN_CHOICES = (('false', 'False'), ('true', 'True'),)

class RecipeFilter(filters.FilterSet):
    author = filters.CharFilter(field_name='author_id')  # , method='filter_author'
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.TypedChoiceFilter(
        choices=BOOLEAN_CHOICES, coerce=strtobool) #, method='filter_is_favorited'
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart', method='filter_is_in_shopping_cart')
    
    def filter_is_in_shopping_cart(self, queryset, name, value):
        print(type(name))
        for q in queryset:
            print(q[name]==value)
        #if value == 0:
        #    return queryset.filter(name=False)
        return queryset.filter(name=value)
    """

    
    def filter_author(self, queryset, name, value):
        if name == 'author':
            query = Recipe.objects.filter(author_id=int(value)).order_by('-id')
            return query
    """
    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
    