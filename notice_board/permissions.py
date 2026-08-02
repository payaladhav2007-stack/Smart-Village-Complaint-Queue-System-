from rest_framework.permissions import BasePermission, SAFE_METHODS


class NoticePermission(BasePermission):
    """
    GS-REG-110: Role-based notice board permissions.

    GET  → Any authenticated user in the same village_city
    POST → Staff or Sarpanch only (approved)
    PATCH/DELETE → 
        Staff: only their own notices, never a Sarpanch's notice
        Sarpanch: their own notices + any Staff notice in their village_city
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.approval_status != 'approved':
            return False
        if request.method in SAFE_METHODS:
            return True
        # POST — only staff or sarpanch can create
        return request.user.role in ['staff', 'sarpanch']

    def has_object_permission(self, request, view, obj):
        user = request.user

        # GET — allowed if same village_city
        if request.method in SAFE_METHODS:
            return obj.village_city == user.village_city

        # PATCH/DELETE
        if user.role == 'sarpanch':
            # Sarpanch can edit/delete their own notices
            # AND any Staff notice in their village_city
            if obj.posted_by == user:
                return True
            if (obj.posted_by.role == 'staff' and
                    obj.village_city == user.village_city):
                return True
            return False

        if user.role == 'staff':
            # Staff can ONLY edit/delete their own notices
            # NEVER a Sarpanch's notice
            if obj.posted_by.role == 'sarpanch':
                return False
            return obj.posted_by == user

        return False