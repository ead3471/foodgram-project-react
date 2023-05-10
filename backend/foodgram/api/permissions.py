from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return True if request.method in SAFE_METHODS else user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_anonymous:
            return False

        return request.user == obj.author
