from rest_framework.permissions import BasePermission


class IsProfileOwner(BasePermission):
    """Allow access only to the owner of the profile object."""

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
