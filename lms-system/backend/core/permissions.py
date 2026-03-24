"""
Core permissions for LMS System.

This module contains base permission classes used across all apps.
"""

from rest_framework import permissions


# === CHUNK: CORE_PERMISSIONS_V1 [CORE] ===
# Описание: Базовые классы разрешений для API.
# Dependencies: none


# [START_IS_AUTHENTICATED_USER]
# ANCHOR: IS_AUTHENTICATED_USER
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - разрешает доступ только аутентифицированным пользователям
# PURPOSE: Проверка аутентификации пользователя.
class IsAuthenticatedUser(permissions.BasePermission):
    """
    Permission class to check if user is authenticated.
    """
    
    message = 'Требуется авторизация.'
    
    # [START_IS_AUTHENTICATED_HAS_PERMISSION]
    # ANCHOR: IS_AUTHENTICATED_HAS_PERMISSION
    # @PreConditions:
    # - request объект запроса
    # - view объект представления
    # @PostConditions:
    # - возвращает True если пользователь аутентифицирован
    # PURPOSE: Проверка прав на уровне представления.
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    # [END_IS_AUTHENTICATED_HAS_PERMISSION]


# [END_IS_AUTHENTICATED_USER]


# [START_IS_ADMIN_OR_READ_ONLY]
# ANCHOR: IS_ADMIN_OR_READ_ONLY
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - разрешает чтение всем, запись только админам
# PURPOSE: Разделение прав на чтение и запись для админов.
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow read-only access to all,
    and write access to admin users only.
    """
    
    message = 'Изменение доступно только администраторам.'
    
    # [START_IS_ADMIN_HAS_PERMISSION]
    # ANCHOR: IS_ADMIN_HAS_PERMISSION
    # @PreConditions:
    # - request объект запроса
    # - view объект представления
    # @PostConditions:
    # - возвращает True для SAFE_METHODS или для админа
    # PURPOSE: Проверка прав на уровне представления.
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )
    # [END_IS_ADMIN_HAS_PERMISSION]


# [END_IS_ADMIN_OR_READ_ONLY]


# [START_IS_OWNER_OR_READ_ONLY]
# ANCHOR: IS_OWNER_OR_READ_ONLY
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - разрешает чтение всем, запись только владельцу объекта
# PURPOSE: Проверка владельца объекта для редактирования.
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow owners to edit their own objects.
    """
    
    message = 'Изменение доступно только владельцу.'
    
    # [START_IS_OWNER_HAS_OBJECT_PERMISSION]
    # ANCHOR: IS_OWNER_HAS_OBJECT_PERMISSION
    # @PreConditions:
    # - request объект запроса
    # - view объект представления
    # - obj объект с атрибутом user
    # @PostConditions:
    # - возвращает True для SAFE_METHODS или если request.user == obj.user
    # PURPOSE: Проверка прав на уровне объекта.
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False
    # [END_IS_OWNER_HAS_OBJECT_PERMISSION]


# [END_IS_OWNER_OR_READ_ONLY]


# [START_IS_ADMIN_OR_OWNER]
# ANCHOR: IS_ADMIN_OR_OWNER
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - разрешает доступ админу или владельцу объекта
# PURPOSE: Проверка прав админа или владельца.
class IsAdminOrOwner(permissions.BasePermission):
    """
    Permission class to allow access to admin or owner.
    """
    
    message = 'Доступ запрещён.'
    
    # [START_IS_ADMIN_OR_OWNER_HAS_OBJECT_PERMISSION]
    # ANCHOR: IS_ADMIN_OR_OWNER_HAS_OBJECT_PERMISSION
    # @PreConditions:
    # - request объект запроса
    # - view объект представления
    # - obj объект с атрибутом user
    # @PostConditions:
    # - возвращает True если пользователь админ или владелец объекта
    # PURPOSE: Проверка прав на уровне объекта для админа или владельца.
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False
    # [END_IS_ADMIN_OR_OWNER_HAS_OBJECT_PERMISSION]


# [END_IS_ADMIN_OR_OWNER]


# === END_CHUNK: CORE_PERMISSIONS_V1 ===