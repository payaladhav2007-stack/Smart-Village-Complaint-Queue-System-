from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, State, District, Taluka, VillageCity


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = [
        'username', 'email', 'phone_number', 'ward_number',
        'role', 'approval_status', 'village_city', 'is_staff',
    ]
    list_filter = ['role', 'approval_status', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'phone_number', 'ward_number']
    ordering = ['ward_number', 'username']

    fieldsets = UserAdmin.fieldsets + (
        ('Rural Parameters', {
            'fields': ('phone_number', 'ward_number', 'role')
        }),
        ('Registration & Access (GS-REG-101)', {
            'fields': (
                'village_city', 'identity_document',
                'approval_status', 'approved_by', 'supervisor',
            )
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rural Parameters', {
            'fields': ('phone_number', 'ward_number', 'role')
        }),
        ('Registration & Access (GS-REG-101)', {
            'fields': (
                'village_city', 'identity_document',
                'approval_status', 'approved_by', 'supervisor',
            )
        }),
    )


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'lgd_code']
    list_filter = ['state']
    search_fields = ['name', 'lgd_code']


@admin.register(Taluka)
class TalukaAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'lgd_code']
    list_filter = ['district']
    search_fields = ['name', 'lgd_code']


@admin.register(VillageCity)
class VillageCityAdmin(admin.ModelAdmin):
    list_display = ['name', 'taluka', 'lgd_code']
    list_filter = ['taluka']
    search_fields = ['name', 'lgd_code']
