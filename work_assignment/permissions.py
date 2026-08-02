from rest_framework.permissions import BasePermission


class IsSarpanch(BasePermission):
    """Only Sarpanch/Nagarsevak can create work assignments."""
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'sarpanch' and
            request.user.approval_status == 'approved'
        )


class IsStaff(BasePermission):
    """Only approved Staff/Officers can view and update their assignments."""
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'staff' and
            request.user.approval_status == 'approved'
        )


class IsSarpanchOrStaff(BasePermission):
    """Sarpanch or Staff — for read access."""
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['sarpanch', 'staff'] and
            request.user.approval_status == 'approved'
        )