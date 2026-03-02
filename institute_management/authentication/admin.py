from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'institute', 'is_approved', 'is_superuser')
    list_filter = ('role', 'is_approved', 'institute', 'is_superuser', 'is_staff')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'institute', 'phone', 'is_approved'),
            'classes': ('wide',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'institute', 'phone', 'is_approved'),
            'classes': ('wide',)
        }),
    )
    
    actions = ['approve_users', 'reject_users', 'make_super_admin']
    
    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
    approve_users.short_description = "Approve selected users"
    
    def reject_users(self, request, queryset):
        queryset.update(is_approved=False)
    reject_users.short_description = "Reject selected users"
    
    def make_super_admin(self, request, queryset):
        queryset.update(role='super_admin', is_approved=True, is_staff=True, is_superuser=True)
    make_super_admin.short_description = "Make selected users Super Admin"