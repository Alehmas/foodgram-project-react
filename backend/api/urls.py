from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet, RecipeViewSet, SubscribeViewSet, TagViewSet, UserFollowViewSet)

app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(
    r'users/subscriptions', SubscribeViewSet, basename='subscribtions')
router_f = DefaultRouter()
router_f.register(r'users', UserFollowViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include(router_f.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
