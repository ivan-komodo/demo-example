"""
User admin configuration for LMS System.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import PasswordResetToken, RefreshToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    
    model = User
    list_display = ['email', 'full_name', 'role', 'is_active', 'is_staff', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'full_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Личная информация'), {'fields': ('full_name', 'role')}),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Важные даты'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    """Admin configuration for RefreshToken model."""
    
    list_display = ['user', 'token', 'expires_at', 'is_revoked', 'created_at']
    list_filter = ['created_at', 'revoked_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['created_at']
    raw_id_fields = ['user']
    
    def is_revoked(self, obj):
        """Check if token is revoked."""
        return obj.is_revoked
    is_revoked.boolean = True
    is_revoked.short_description = _('Отозван')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin configuration for PasswordResetToken model."""
    
    list_display = ['user', 'token', 'expires_at', 'is_used', 'created_at']
    list_filter = ['created_at', 'used_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['created_at']
    raw_id_fields = ['user']
    
    def is_used(self, obj):
        """Check if token is used."""
        return obj.is_used
    is_used.boolean = True
    is_used.short_description = _('Использован')