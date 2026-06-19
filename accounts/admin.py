from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'phone_number', 'ward_number', 'role', 'is_staff']
    list_filter = ['role', 'ward_number', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'phone_number', 'ward_number']
    ordering = ['ward_number', 'username']

    fieldsets = UserAdmin.fieldsets + (
        ('Rural Parameters', {'fields': ('phone_number', 'ward_number', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rural Parameters', {'fields': ('phone_number', 'ward_number', 'role')}),
    )