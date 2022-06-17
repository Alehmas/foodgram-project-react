from django.contrib import admin
from users.models import Follow, User

from .models import Favorite, Ingredient, Recipe, Shopping, Tag


class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'username', 'last_name', 'email')
    list_filter = ('email', 'username')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'is_favorited_count')
    list_filter = ('name', 'tags', 'author')

    def is_favorited_count(self, obj):
        return Favorite.objects.filter(**{'recipe': obj}).count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(User, UserAdmin)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(Shopping)
