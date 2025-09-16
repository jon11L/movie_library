from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrIsAuthenticatedReadOnly(BasePermission):
    """
    - Custom permission to only allow admin and staffs to perform POST/PUT operation. (Full access) \n
    - authenticated users can GET/readonly operation (Restricted access) \n
    - unauthenticated users access not allowed. Require some Authentication.\n
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if not request.user or not request.user.is_authenticated:
            return False # No access for anonymous user /requires authentication
        
        if request.method in SAFE_METHODS:
            return True

        # Write permissions for objects (POST/create PUT/update an object) are only allowed to the admin and staff
        return request.user and request.user.is_staff
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if not request.user or not request.user.is_authenticated:
            return False # No access for anonymous user /requires authentication

        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the admin and staff
        return request.user and request.user.is_staff
