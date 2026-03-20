"""
User permissions for LMS System.

This module contains custom permissions for user management.
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission to only allow admin users.
    """
    
    message = 'Доступ разрешён только администраторам.'
    
    def has_permission(self, request, view):
        """Check if user is admin."""
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsTrainerUser(permissions.BasePermission):
    """
    Permission to only allow trainer users.
    """
    
    message = 'Доступ разрешён только тренерам.'
    
    def has_permission(self, request, view):
        """Check if user is trainer."""
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_trainer or request.user.is_admin)
        )


class IsLearnerUser(permissions.BasePermission):
    """
    Permission to only allow learner users.
    """
    
    message = 'Доступ разрешён только слушателям.'
    
    def has_permission(self, request, view):
        """Check if user is learner."""
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_learner
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of an object or admin users.
    """
    
    message = 'Доступ разрешён только владельцу или администратору.'
    
    def has_object_permission(self, request, view, obj):
        """Check if user is owner or admin."""
        if request.user.is_admin:
            return True
        
        # Check if object has user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if object is a User instance
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
        
        return False


class IsSameUserOrAdmin(permissions.BasePermission):
    """
    Permission to only allow same user or admin users.
    Used for User model.
    """
    
    message = 'Доступ разрешён только к своей учётной записи или администратору.'
    
    def has_object_permission(self, request, view, obj):
        """Check if user is same or admin."""
        if request.user.is_admin:
            return True
        return obj == request.user