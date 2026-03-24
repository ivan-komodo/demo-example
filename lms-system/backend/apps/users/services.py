"""
User services for LMS System.

This module contains business logic for user management.
"""

from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import PasswordResetToken, RefreshToken

User = get_user_model()


# === CHUNK: USER_SERVICES_V1 [USER_MANAGEMENT] ===
# Описание: Сервисы для управления пользователями и токенами.
# Dependencies: USER_MODEL_V1


# [START_USER_SERVICE_CLASS]
# ANCHOR: USER_SERVICE_CLASS
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет статические методы для управления пользователями
# PURPOSE: Инкапсуляция бизнес-логики управления пользователями.
class UserService:
    """Service for user management."""
    
    # [START_CREATE_USER_SERVICE]
    # ANCHOR: CREATE_USER_SERVICE
    # @PreConditions:
    # - email: непустая строка с валидным email-форматом
    # - password: непустая строка
    # @PostConditions:
    # - возвращает созданный экземпляр User с хешированным паролем
    # PURPOSE: Создание нового пользователя через UserManager.
    @staticmethod
    def create_user(email: str, password: str, full_name: str = '', role: str = 'learner') -> User:
        """
        Create a new user.
        
        Args:
            email: User email
            password: User password
            full_name: User full name
            role: User role (admin, trainer, learner)
            
        Returns:
            Created User instance
        """
        return User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            role=role,
        )
    # [END_CREATE_USER_SERVICE]
    
    # [START_DEACTIVATE_USER]
    # ANCHOR: DEACTIVATE_USER
    # @PreConditions:
    # - user_id: целое положительное число
    # @PostConditions:
    # - возвращает True если пользователь найден и деактивирован
    # - возвращает False если пользователь не найден
    # PURPOSE: Деактивация учётной записи пользователя.
    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        """
        Deactivate a user.
        
        Args:
            user_id: User ID to deactivate
            
        Returns:
            True if user was deactivated, False otherwise
        """
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save(update_fields=['is_active'])
            return True
        except User.DoesNotExist:
            return False
    # [END_DEACTIVATE_USER]
    
    # [START_ACTIVATE_USER]
    # ANCHOR: ACTIVATE_USER
    # @PreConditions:
    # - user_id: целое положительное число
    # @PostConditions:
    # - возвращает True если пользователь найден и активирован
    # - возвращает False если пользователь не найден
    # PURPOSE: Активация учётной записи пользователя.
    @staticmethod
    def activate_user(user_id: int) -> bool:
        """
        Activate a user.
        
        Args:
            user_id: User ID to activate
            
        Returns:
            True if user was activated, False otherwise
        """
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save(update_fields=['is_active'])
            return True
        except User.DoesNotExist:
            return False
    # [END_ACTIVATE_USER]


# [END_USER_SERVICE_CLASS]


# [START_TOKEN_SERVICE_CLASS]
# ANCHOR: TOKEN_SERVICE_CLASS
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет статические методы для управления токенами
# PURPOSE: Инкапсуляция бизнес-логики управления токенами сброса пароля и refresh-токенами.
class TokenService:
    """Service for token management."""
    
    # [START_CREATE_PASSWORD_RESET_TOKEN]
    # ANCHOR: CREATE_PASSWORD_RESET_TOKEN
    # @PreConditions:
    # - user: экземпляр User, существующий в БД
    # @PostConditions:
    # - предыдущие неиспользованные токены пользователя помечены как использованные
    # - возвращает новый PasswordResetToken с expires_at через 24 часа
    # PURPOSE: Создание токена для сброса пароля с инвалидацией старых токенов.
    @staticmethod
    def create_password_reset_token(user: User) -> PasswordResetToken:
        """
        Create a password reset token for a user.
        
        Args:
            user: User instance
            
        Returns:
            Created PasswordResetToken instance
        """
        # Invalidate previous tokens
        PasswordResetToken.objects.filter(
            user=user,
            used_at__isnull=True,
        ).update(used_at=timezone.now())
        
        return PasswordResetToken.objects.create(
            user=user,
            token=PasswordResetToken.objects.make_random_password(64),
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )
    # [END_CREATE_PASSWORD_RESET_TOKEN]
    
    # [START_VALIDATE_PASSWORD_RESET_TOKEN]
    # ANCHOR: VALIDATE_PASSWORD_RESET_TOKEN
    # @PreConditions:
    # - token: непустая строка
    # @PostConditions:
    # - при валидном токене возвращает (User, None)
    # - при невалидном токене возвращает (None, error_message)
    # PURPOSE: Валидация токена сброса пароля.
    @staticmethod
    def validate_password_reset_token(token: str) -> tuple[User | None, str | None]:
        """
        Validate a password reset token.
        
        Args:
            token: Token string
            
        Returns:
            Tuple of (User instance or None, error message or None)
        """
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return None, 'Неверный токен.'
        
        if reset_token.is_used:
            return None, 'Токен уже использован.'
        
        if reset_token.is_expired:
            return None, 'Токен истёк.'
        
        return reset_token.user, None
    # [END_VALIDATE_PASSWORD_RESET_TOKEN]
    
    # [START_REVOKE_ALL_REFRESH_TOKENS]
    # ANCHOR: REVOKE_ALL_REFRESH_TOKENS
    # @PreConditions:
    # - user: экземпляр User, существующий в БД
    # @PostConditions:
    # - все активные refresh-токены пользователя помечены как отозванные
    # - возвращает количество отозванных токенов
    # PURPOSE: Отзыв всех refresh-токенов пользователя (logout из всех сессий).
    @staticmethod
    def revoke_all_refresh_tokens(user: User) -> int:
        """
        Revoke all refresh tokens for a user.
        
        Args:
            user: User instance
            
        Returns:
            Number of tokens revoked
        """
        return RefreshToken.objects.filter(
            user=user,
            revoked_at__isnull=True,
        ).update(revoked_at=timezone.now())
    # [END_REVOKE_ALL_REFRESH_TOKENS]


# [END_TOKEN_SERVICE_CLASS]


# === END_CHUNK: USER_SERVICES_V1 ===