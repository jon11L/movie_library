from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrIsAuthenticatedReadOnly(BasePermission):
    """
    - Custom permission to only allow admin and staffs to perform POST/PUT operation. (Full access) \n
    - authenticated users can GET/readonly operation (Restricted access) \n
    - unauthenticated users access not allowed. Require some Authentication.\n
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if not request.user or not request.user.is_authenticated:
            return False # No access for anonymous user /requires authentication

        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the admin and staff
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # if not request.user or not request.user.is_authenticated:
        if not request.user or not request.user.is_authenticated:
            return False # No access for anonymous user /requires authentication
        
        if request.method in SAFE_METHODS:
            return True

        # Write permissions for objects (POST/create PUT/update an object) are only allowed to the admin and staff
        return request.user and request.user.is_staff




class IsAdminOrOwner(BasePermission):
    """
    - Custom permission:
    - admin and staffs to perform ALL operation on any objects. (Full access) \n
    - authenticated users can GET/CREATE/PUT/DELETE (Restricted access to their own object) \n
    - Anonymous/unauthenticated users access not allowed. Require some Authentication.\n
    """
    
    # list view
    def has_permission(self, request, view): 
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if not request.user or not request.user.is_authenticated:
            return False # No access for anonymous user /requires authentication

        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin,staff & authenticated users owners of the current object
        return True


    # detailled view/single object
    def has_object_permission(self, request, view, obj): 
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if not request.user or not request.user.is_authenticated:
            return False # No access for anonymous user /requires authentication
        
        if request.method in SAFE_METHODS:
            return True

        # Write permissions for objects (POST/create PUT/update an object) are only allowed to the admin and staff
        # return request.user and request.user.is_staff
        if request.user.is_staff:
            return True
        
        return obj.user == request.user