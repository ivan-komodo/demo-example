"""
User services for LMS System.

This module contains business logic for user management.
"""

from django.contrib.auth import get_user_model
from django.utils import timezone

from core.utils import log_line
from .models import PasswordResetToken, RefreshToken

User = get_user_model()


# === CHUNK: USER_SERVICES_V1 [USER_MANAGEMENT] ===
# Описание: Сервисы для управления пользователями и токенами.
# Dependencies: USER_MODEL_V1


# [START_CREATE_USER_SERVICE]
"""
ANCHOR: CREATE_USER_SERVICE
PURPOSE: Создание нового пользователя через UserManager.

@PreConditions:
- email: непустая строка с валидным email-форматом
- password: непустая строка
- full_name: опциональная строка
- role: опциональная строка ('admin', 'trainer', 'learner')

@PostConditions:
- возвращает созданный экземпляр User с хешированным паролем
- email нормализован

@Invariants:
- пароль всегда хешируется через set_password
- email всегда нормализуется

@SideEffects:
- создание записи в БД (User)
- логирование операции

@ForbiddenChanges:
- использование UserManager для создания (не прямой insert)
"""
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
    log_line("users", "DEBUG", "create_user", "CREATE_USER_SERVICE", "ENTRY", {
        "email": email,
        "role": role,
    })
    
    user = User.objects.create_user(
        email=email,
        password=password,
        full_name=full_name,
        role=role,
    )
    
    log_line("users", "INFO", "create_user", "CREATE_USER_SERVICE", "STATE_CHANGE", {
        "action": "user_created",
        "user_id": user.id,
        "email": email,
        "role": role,
    })
    log_line("users", "DEBUG", "create_user", "CREATE_USER_SERVICE", "EXIT", {
        "result": "success",
        "user_id": user.id,
    })
    
    return user
# [END_CREATE_USER_SERVICE]


# [START_DEACTIVATE_USER]
"""
ANCHOR: DEACTIVATE_USER
PURPOSE: Деактивация учётной записи пользователя.

@PreConditions:
- user_id: целое положительное число

@PostConditions:
- возвращает True если пользователь найден и деактивирован
- возвращает False если пользователь не найден

@Invariants:
- только поле is_active изменяется
- другие поля пользователя не затрагиваются

@SideEffects:
- обновление is_active=False в БД
- логирование операции

@ForbiddenChanges:
- только деактивация (не удаление пользователя)
"""
def deactivate_user(user_id: int) -> bool:
    """
    Deactivate a user.
    
    Args:
        user_id: User ID to deactivate
        
    Returns:
        True if user was deactivated, False otherwise
    """
    log_line("users", "DEBUG", "deactivate_user", "DEACTIVATE_USER", "ENTRY", {
        "user_id": user_id,
    })
    
    try:
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        log_line("users", "INFO", "deactivate_user", "DEACTIVATE_USER", "STATE_CHANGE", {
            "action": "user_deactivated",
            "user_id": user_id,
            "email": user.email,
        })
        log_line("users", "DEBUG", "deactivate_user", "DEACTIVATE_USER", "EXIT", {
            "result": "success",
        })
        return True
    except User.DoesNotExist:
        log_line("users", "WARN", "deactivate_user", "DEACTIVATE_USER", "ERROR", {
            "reason": "user_not_found",
            "user_id": user_id,
        })
        log_line("users", "DEBUG", "deactivate_user", "DEACTIVATE_USER", "EXIT", {
            "result": "not_found",
        })
        return False
# [END_DEACTIVATE_USER]


# [START_ACTIVATE_USER]
"""
ANCHOR: ACTIVATE_USER
PURPOSE: Активация учётной записи пользователя.

@PreConditions:
- user_id: целое положительное число

@PostConditions:
- возвращает True если пользователь найден и активирован
- возвращает False если пользователь не найден

@Invariants:
- только поле is_active изменяется
- другие поля пользователя не затрагиваются

@SideEffects:
- обновление is_active=True в БД
- логирование операции

@ForbiddenChanges:
- только активация (не создание нового пользователя)
"""
def activate_user(user_id: int) -> bool:
    """
    Activate a user.
    
    Args:
        user_id: User ID to activate
        
    Returns:
        True if user was activated, False otherwise
    """
    log_line("users", "DEBUG", "activate_user", "ACTIVATE_USER", "ENTRY", {
        "user_id": user_id,
    })
    
    try:
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save(update_fields=['is_active'])
        
        log_line("users", "INFO", "activate_user", "ACTIVATE_USER", "STATE_CHANGE", {
            "action": "user_activated",
            "user_id": user_id,
            "email": user.email,
        })
        log_line("users", "DEBUG", "activate_user", "ACTIVATE_USER", "EXIT", {
            "result": "success",
        })
        return True
    except User.DoesNotExist:
        log_line("users", "WARN", "activate_user", "ACTIVATE_USER", "ERROR", {
            "reason": "user_not_found",
            "user_id": user_id,
        })
        log_line("users", "DEBUG", "activate_user", "ACTIVATE_USER", "EXIT", {
            "result": "not_found",
        })
        return False
# [END_ACTIVATE_USER]


# [START_CREATE_PASSWORD_RESET_TOKEN]
"""
ANCHOR: CREATE_PASSWORD_RESET_TOKEN
PURPOSE: Создание токена для сброса пароля с инвалидацией старых токенов.

@PreConditions:
- user: экземпляр User, существующий в БД

@PostConditions:
- предыдущие неиспользованные токены пользователя помечены как использованные
- возвращает новый PasswordResetToken с expires_at через 24 часа

@Invariants:
- всегда только один активный токен сброса пароля на пользователя

@SideEffects:
- обновление used_at старых токенов
- создание нового PasswordResetToken в БД
- логирование операции

@ForbiddenChanges:
- инвалидация старых токенов (обязательная)
- срок жизни токена 24 часа
"""
def create_password_reset_token(user: User) -> PasswordResetToken:
    """
    Create a password reset token for a user.
    
    Args:
        user: User instance
        
    Returns:
        Created PasswordResetToken instance
    """
    log_line("users", "DEBUG", "create_password_reset_token", "CREATE_PASSWORD_RESET_TOKEN", "ENTRY", {
        "user_id": user.id,
        "email": user.email,
    })
    
    invalidated_count = PasswordResetToken.objects.filter(
        user=user,
        used_at__isnull=True,
    ).update(used_at=timezone.now())
    
    log_line("users", "DEBUG", "create_password_reset_token", "CREATE_PASSWORD_RESET_TOKEN", "BRANCH", {
        "invalidated_tokens": invalidated_count,
    })
    
    token = PasswordResetToken.objects.create(
        user=user,
        token=PasswordResetToken.objects.make_random_password(64),
        expires_at=timezone.now() + timezone.timedelta(hours=24)
    )
    
    log_line("users", "INFO", "create_password_reset_token", "CREATE_PASSWORD_RESET_TOKEN", "STATE_CHANGE", {
        "action": "reset_token_created",
        "user_id": user.id,
        "expires_in_hours": 24,
    })
    log_line("users", "DEBUG", "create_password_reset_token", "CREATE_PASSWORD_RESET_TOKEN", "EXIT", {
        "result": "success",
    })
    
    return token
# [END_CREATE_PASSWORD_RESET_TOKEN]


# [START_VALIDATE_PASSWORD_RESET_TOKEN]
"""
ANCHOR: VALIDATE_PASSWORD_RESET_TOKEN
PURPOSE: Валидация токена сброса пароля.

@PreConditions:
- token: непустая строка

@PostConditions:
- при валидном токене возвращает (User, None)
- при невалидном токене возвращает (None, error_message)

@Invariants:
- не изменяет состояние токена

@SideEffects:
- чтение из БД
- логирование операции

@ForbiddenChanges:
- не помечать токен как использованный (это делается отдельно)
"""
def validate_password_reset_token(token: str) -> tuple[User | None, str | None]:
    """
    Validate a password reset token.
    
    Args:
        token: Token string
        
    Returns:
        Tuple of (User instance or None, error message or None)
    """
    log_line("users", "DEBUG", "validate_password_reset_token", "VALIDATE_PASSWORD_RESET_TOKEN", "ENTRY", {
        "token_prefix": token[:10] + "..." if token else None,
    })
    
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        log_line("users", "WARN", "validate_password_reset_token", "VALIDATE_PASSWORD_RESET_TOKEN", "DECISION", {
            "decision": "token_not_found",
        })
        log_line("users", "DEBUG", "validate_password_reset_token", "VALIDATE_PASSWORD_RESET_TOKEN", "EXIT", {
            "result": "invalid",
            "error": "token_not_found",
        })
        return None, 'Неверный токен.'
    
    if reset_token.is_used:
        log_line("users", "WARN", "validate_password_reset_token", "VALIDATE_PASSWORD_RESET_TOKEN", "DECISION", {
            "decision": "token_used",
            "user_id": reset_token.user_id,
        })
        log_line("users", "DEBUG", "validate_password_reset_token", "VALIDATE_PASSWORD_RESET_TOKEN", "EXIT", {
            "result": "invalid",
            "error": "token_used",
        })
        return None, 'Токен уже использован.'
    
    if reset_token.is_expired:
        log_line("users", "WARN", "validate_password_reset_token", "VALIDATE_PASSWORD_RESET_TOKEN", "DECISION", {
            "decision": "token_expired",
            "user_id": reset_token.user_id,
        })
        log_line("users", "DEBUG", "validate_password_reset_token", "VALIDATE_PASSWORD_RESET_TOKEN", "EXIT", {
            "result": "invalid",
            "error": "token_expired",
        })
        return None, 'Токен истёк.'
    
    log_line("users", "DEBUG", "validate_password_reset_token", "VALIDATE_PASSWORD_RESET_TOKEN", "CHECK", {
        "check": "token_valid",
        "user_id": reset_token.user_id,
    })
    log_line("users", "DEBUG", "validate_password_reset_token", "VALIDATE_PASSWORD_RESET_TOKEN", "EXIT", {
        "result": "valid",
        "user_id": reset_token.user_id,
    })
    
    return reset_token.user, None
# [END_VALIDATE_PASSWORD_RESET_TOKEN]


# [START_REVOKE_ALL_REFRESH_TOKENS]
"""
ANCHOR: REVOKE_ALL_REFRESH_TOKENS
PURPOSE: Отзыв всех refresh-токенов пользователя (logout из всех сессий).

@PreConditions:
- user: экземпляр User, существующий в БД

@PostConditions:
- все активные refresh-токены пользователя помечены как отозванные
- возвращает количество отозванных токенов

@Invariants:
- только токены конкретного пользователя отзываются

@SideEffects:
- обновление revoked_at в БД для токенов пользователя
- логирование операции

@ForbiddenChanges:
- отзыв только активных (revoked_at__isnull=True) токенов
"""
def revoke_all_refresh_tokens(user: User) -> int:
    """
    Revoke all refresh tokens for a user.
    
    Args:
        user: User instance
        
    Returns:
        Number of tokens revoked
    """
    log_line("users", "DEBUG", "revoke_all_refresh_tokens", "REVOKE_ALL_REFRESH_TOKENS", "ENTRY", {
        "user_id": user.id,
    })
    
    count = RefreshToken.objects.filter(
        user=user,
        revoked_at__isnull=True,
    ).update(revoked_at=timezone.now())
    
    log_line("users", "INFO", "revoke_all_refresh_tokens", "REVOKE_ALL_REFRESH_TOKENS", "STATE_CHANGE", {
        "action": "tokens_revoked",
        "user_id": user.id,
        "count": count,
    })
    log_line("users", "DEBUG", "revoke_all_refresh_tokens", "REVOKE_ALL_REFRESH_TOKENS", "EXIT", {
        "result": "success",
        "count": count,
    })
    
    return count
# [END_REVOKE_ALL_REFRESH_TOKENS]


# === END_CHUNK: USER_SERVICES_V1 ===