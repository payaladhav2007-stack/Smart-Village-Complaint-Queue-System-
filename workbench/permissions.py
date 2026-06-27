from rest_framework.permissions import BasePermission

class IsStaffOrAdmin(BasePermission):
    """
    Restricts access to staff and admin roles only.
    Blocks citizen-level users from workbench endpoints.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['staff', 'admin']
