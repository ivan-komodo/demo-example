"""
Core permissions for LMS System.

This module contains base permission classes used across all apps.
"""

from rest_framework import permissions


class IsAuthenticatedUser(permissions.BasePermission):
    """
    Permission class to check if user is authenticated.
    """
    
    message = 'Требуется авторизация.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow read-only access to all,
    and write access to admin users only.
    """
    
    message = 'Изменение доступно только администраторам.'
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow owners to edit their own objects.
    """
    
    message = 'Изменение доступно только владельцу.'
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsAdminOrOwner(permissions.BasePermission):
    """
    Permission class to allow access to admin or owner.
    """
    
    message = 'Доступ запрещён.'
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False