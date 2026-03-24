"""
User permissions for LMS System.

This module contains custom permissions for user management.
"""

from rest_framework import permissions


# === CHUNK: USER_PERMISSIONS_V1 [AUTHORIZATION] ===
# Описание: Кастомные разрешения для управления доступом пользователей.
# Dependencies: none


# [START_IS_ADMIN_USER]
# ANCHOR: IS_ADMIN_USER
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - has_permission возвращает True только для аутентифицированных администраторов
# PURPOSE: Разрешение доступа только для пользователей с ролью admin.
class IsAdminUser(permissions.BasePermission):
    """
    Permission to only allow admin users.
    """
    
    message = 'Доступ разрешён только администраторам.'
    
    # [START_HAS_PERMISSION_ADMIN]
    # ANCHOR: HAS_PERMISSION_ADMIN
    # @PreConditions:
    # - request: объект запроса DRF
    # - view: объект представления DRF
    # @PostConditions:
    # - возвращает True если пользователь аутентифицирован и is_admin
    # - иначе возвращает False
    # PURPOSE: Проверка прав администратора для запроса.
    def has_permission(self, request, view):
        """Check if user is admin."""
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )
    # [END_HAS_PERMISSION_ADMIN]


# [END_IS_ADMIN_USER]


# [START_IS_TRAINER_USER]
# ANCHOR: IS_TRAINER_USER
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - has_permission возвращает True для тренеров и администраторов
# PURPOSE: Разрешение доступа для тренеров и администраторов.
class IsTrainerUser(permissions.BasePermission):
    """
    Permission to only allow trainer users.
    """
    
    message = 'Доступ разрешён только тренерам.'
    
    # [START_HAS_PERMISSION_TRAINER]
    # ANCHOR: HAS_PERMISSION_TRAINER
    # @PreConditions:
    # - request: объект запроса DRF
    # - view: объект представления DRF
    # @PostConditions:
    # - возвращает True если пользователь is_trainer или is_admin
    # - иначе возвращает False
    # PURPOSE: Проверка прав тренера или администратора для запроса.
    def has_permission(self, request, view):
        """Check if user is trainer."""
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_trainer or request.user.is_admin)
        )
    # [END_HAS_PERMISSION_TRAINER]


# [END_IS_TRAINER_USER]


# [START_IS_LEARNER_USER]
# ANCHOR: IS_LEARNER_USER
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - has_permission возвращает True только для слушателей
# PURPOSE: Разрешение доступа только для пользователей с ролью learner.
class IsLearnerUser(permissions.BasePermission):
    """
    Permission to only allow learner users.
    """
    
    message = 'Доступ разрешён только слушателям.'
    
    # [START_HAS_PERMISSION_LEARNER]
    # ANCHOR: HAS_PERMISSION_LEARNER
    # @PreConditions:
    # - request: объект запроса DRF
    # - view: объект представления DRF
    # @PostConditions:
    # - возвращает True если пользователь аутентифицирован и is_learner
    # - иначе возвращает False
    # PURPOSE: Проверка прав слушателя для запроса.
    def has_permission(self, request, view):
        """Check if user is learner."""
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_learner
        )
    # [END_HAS_PERMISSION_LEARNER]


# [END_IS_LEARNER_USER]


# [START_IS_OWNER_OR_ADMIN]
# ANCHOR: IS_OWNER_OR_ADMIN
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - has_object_permission возвращает True для владельца объекта или администратора
# PURPOSE: Разрешение доступа владельцу объекта или администратору.
class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of an object or admin users.
    """
    
    message = 'Доступ разрешён только владельцу или администратору.'
    
    # [START_HAS_OBJECT_PERMISSION_OWNER]
    # ANCHOR: HAS_OBJECT_PERMISSION_OWNER
    # @PreConditions:
    # - request: объект запроса DRF
    # - view: объект представления DRF
    # - obj: объект модели для проверки прав
    # @PostConditions:
    # - возвращает True если пользователь is_admin или владелец объекта
    # - иначе возвращает False
    # PURPOSE: Проверка прав на объект: владелец или администратор.
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
    # [END_HAS_OBJECT_PERMISSION_OWNER]


# [END_IS_OWNER_OR_ADMIN]


# [START_IS_SAME_USER_OR_ADMIN]
# ANCHOR: IS_SAME_USER_OR_ADMIN
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - has_object_permission возвращает True если obj == request.user или is_admin
# PURPOSE: Разрешение доступа к своей учётной записи или администратору.
class IsSameUserOrAdmin(permissions.BasePermission):
    """
    Permission to only allow same user or admin users.
    Used for User model.
    """
    
    message = 'Доступ разрешён только к своей учётной записи или администратору.'
    
    # [START_HAS_OBJECT_PERMISSION_SAME_USER]
    # ANCHOR: HAS_OBJECT_PERMISSION_SAME_USER
    # @PreConditions:
    # - request: объект запроса DRF
    # - view: объект представления DRF
    # - obj: объект User для проверки прав
    # @PostConditions:
    # - возвращает True если пользователь is_admin или obj == request.user
    # - иначе возвращает False
    # PURPOSE: Проверка прав на User-объект: сам пользователь или администратор.
    def has_object_permission(self, request, view, obj):
        """Check if user is same or admin."""
        if request.user.is_admin:
            return True
        return obj == request.user
    # [END_HAS_OBJECT_PERMISSION_SAME_USER]


# [END_IS_SAME_USER_OR_ADMIN]


# === END_CHUNK: USER_PERMISSIONS_V1 ===