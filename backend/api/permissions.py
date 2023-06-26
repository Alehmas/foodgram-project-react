from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrAuthor(BasePermission):
    """Allow any action to the administrator and user."""

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user
                or request.user.is_superuser)


class IsAdminOrAuthorOrReadOnly(BasePermission):
    """Allow any action to the author and administrator or read to any user."""

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user
                or request.user.is_superuser
                or request.user.is_staff)
