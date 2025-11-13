from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    Read-only access for non-admin users.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Read-only access for non-owners.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        return obj.owner == request.user

class IsAssignedOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow assigned users or admin to access an object.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users have full permissions
        if request.user and request.user.is_staff:
            return True
            
        # Check if the user is assigned to the object
        if hasattr(obj, 'assigned_to'):
            return obj.assigned_to == request.user
            
        # For models without assigned_to field, check ownership
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
            
        return False
