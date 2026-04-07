"""
User models for LMS System.

This module contains the custom User model and related models
for authentication and user management.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.utils import log_line


# === CHUNK: USER_MANAGER_V1 [AUTHENTICATION] ===
# Описание: Менеджер для создания пользователей и суперпользователей.
# Dependencies: none
# [START_USER_MANAGER_CLASS]
"""
ANCHOR: USER_MANAGER_CLASS
PURPOSE: Кастомный менеджер для создания пользователей и суперпользователей.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет методы create_user и create_superuser

@Invariants:
- email всегда нормализуется перед сохранением
- пароль всегда хешируется через set_password

@SideEffects:
- создание записей в БД при вызове create_* методов

@ForbiddenChanges:
- использование AbstractBaseUser API
"""
class UserManager(BaseUserManager):
    """Custom user manager for User model."""
    
    # [START_CREATE_USER]
    """
    ANCHOR: CREATE_USER
    PURPOSE: Создание обычного пользователя с указанным email и паролем.
    
    @PreConditions:
    - email: непустая строка с валидным email-форматом
    - password: строка (может быть None для пользователя без пароля)
    
    @PostConditions:
    - возвращает созданный экземпляр User с нормализованным email
    - при отсутствии email выбрасывает ValueError
    
    @Invariants:
    - email всегда нормализуется
    - пароль всегда хешируется
    
    @SideEffects:
    - создание записи User в БД
    - логирование операции
    
    @ForbiddenChanges:
    - бросание ValueError при отсутствии email
    """
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        log_line("users", "DEBUG", "create_user", "CREATE_USER", "ENTRY", {
            "email": email,
        })
        
        if not email:
            log_line("users", "ERROR", "create_user", "CREATE_USER", "ERROR", {
                "reason": "email_required",
            })
            raise ValueError(_('Email обязателен'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        log_line("users", "INFO", "create_user", "CREATE_USER", "STATE_CHANGE", {
            "action": "user_created",
            "user_id": user.id,
            "email": email,
        })
        log_line("users", "DEBUG", "create_user", "CREATE_USER", "EXIT", {
            "result": "success",
            "user_id": user.id,
        })
        
        return user
    # [END_CREATE_USER]
    
    # [START_CREATE_SUPERUSER]
    """
    ANCHOR: CREATE_SUPERUSER
    PURPOSE: Создание суперпользователя с полными правами доступа.
    
    @PreConditions:
    - email: непустая строка с валидным email-форматом
    - password: непустая строка
    - extra_fields: опциональные поля (is_staff, is_superuser, is_active, role)
    
    @PostConditions:
    - возвращает созданный экземпляр User с is_staff=True, is_superuser=True
    - при некорректных флагах выбрасывает ValueError
    
    @Invariants:
    - is_staff и is_superuser всегда True для суперпользователя
    - role по умолчанию 'admin'
    
    @SideEffects:
    - создание записи User в БД
    - логирование операции
    
    @ForbiddenChanges:
    - проверка is_staff=True и is_superuser=True
    """
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        log_line("users", "DEBUG", "create_superuser", "CREATE_SUPERUSER", "ENTRY", {
            "email": email,
        })
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            log_line("users", "ERROR", "create_superuser", "CREATE_SUPERUSER", "ERROR", {
                "reason": "is_staff_must_be_true",
            })
            raise ValueError(_('Суперпользователь должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            log_line("users", "ERROR", "create_superuser", "CREATE_SUPERUSER", "ERROR", {
                "reason": "is_superuser_must_be_true",
            })
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True.'))
        
        user = self.create_user(email, password, **extra_fields)
        
        log_line("users", "INFO", "create_superuser", "CREATE_SUPERUSER", "STATE_CHANGE", {
            "action": "superuser_created",
            "user_id": user.id,
            "email": email,
        })
        log_line("users", "DEBUG", "create_superuser", "CREATE_SUPERUSER", "EXIT", {
            "result": "success",
            "user_id": user.id,
        })
        
        return user
    # [END_CREATE_SUPERUSER]
    
    # [START_GET_BY_NATURAL_KEY]
    """
    ANCHOR: GET_BY_NATURAL_KEY
    PURPOSE: Получение пользователя по естественному ключу (email).
    
    @PreConditions:
    - email: строка для поиска пользователя
    
    @PostConditions:
    - возвращает экземпляр User с указанным email
    - при отсутствии пользователя выбрасывает DoesNotExist
    
    @Invariants:
    - использует email как natural key
    
    @SideEffects:
    - чтение из БД
    - логирование операции
    
    @ForbiddenChanges:
    - использование get(email=email)
    """
    def get_by_natural_key(self, email):
        """Get user by natural key (email)."""
        log_line("users", "DEBUG", "get_by_natural_key", "GET_BY_NATURAL_KEY", "ENTRY", {
            "email": email,
        })
        
        user = self.get(email=email)
        
        log_line("users", "DEBUG", "get_by_natural_key", "GET_BY_NATURAL_KEY", "EXIT", {
            "result": "found",
            "user_id": user.id,
        })
        
        return user
    # [END_GET_BY_NATURAL_KEY]
# [END_USER_MANAGER_CLASS]


# === END_CHUNK: USER_MANAGER_V1 ===


# === CHUNK: USER_MODEL_V1 [AUTHENTICATION] ===
# Описание: Основная модель пользователя системы с ролями admin/trainer/learner.
# Dependencies: USER_MANAGER_V1
# [START_USER_MODEL]
"""
ANCHOR: USER_MODEL
PURPOSE: Основная модель пользователя системы с ролями admin/trainer/learner.

@PreConditions:
- нет нетривиальных предусловий для модели

@PostConditions:
- использует email как уникальный идентификатор
- поддерживает три роли: admin, trainer, learner

@Invariants:
- email всегда уникален
- role всегда из допустимых значений

@SideEffects:
- нет побочных эффектов на уровне класса

@ForbiddenChanges:
- USERNAME_FIELD = 'email'
- REQUIRED_FIELDS = ['full_name']
"""
class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for LMS System.
    
    Uses email as the unique identifier instead of username.
    Supports three roles: admin, trainer, learner.
    """
    
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Администратор')
        TRAINER = 'trainer', _('Тренер')
        LEARNER = 'learner', _('Слушатель')
    
    email = models.EmailField(
        _('Email'),
        unique=True,
        db_index=True,
        error_messages={
            'unique': _('Пользователь с таким email уже существует.'),
        },
    )
    full_name = models.CharField(_('ФИО'), max_length=255, blank=True)
    role = models.CharField(
        _('Роль'),
        max_length=20,
        choices=Role.choices,
        default=Role.LEARNER,
    )
    is_active = models.BooleanField(_('Активен'), default=True)
    is_staff = models.BooleanField(_('Персонал'), default=False)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['-created_at']
    
    # [START_USER_STR]
    """
    ANCHOR: USER_STR
    PURPOSE: Строковое представление пользователя для отображения в админке и логах.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - возвращает email пользователя
    
    @Invariants:
    - всегда возвращает строку
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - возвращаемое значение (email)
    """
    def __str__(self):
        return self.email
    # [END_USER_STR]
    
    # [START_GET_FULL_NAME]
    """
    ANCHOR: GET_FULL_NAME
    PURPOSE: Получение полного имени пользователя или email как fallback.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - возвращает full_name если заполнено, иначе email
    
    @Invariants:
    - всегда возвращает непустую строку
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - fallback на email при пустом full_name
    """
    def get_full_name(self):
        """Return the full name of the user."""
        return self.full_name or self.email
    # [END_GET_FULL_NAME]
    
    # [START_GET_SHORT_NAME]
    """
    ANCHOR: GET_SHORT_NAME
    PURPOSE: Получение короткого имени пользователя для отображения.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - возвращает часть email до символа @
    
    @Invariants:
    - всегда возвращает строку
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - формат (часть email до @)
    """
    def get_short_name(self):
        """Return the short name of the user."""
        return self.email.split('@')[0]
    # [END_GET_SHORT_NAME]
    
    # [START_IS_ADMIN_PROPERTY]
    """
    ANCHOR: IS_ADMIN_PROPERTY
    PURPOSE: Проверка является ли пользователь администратором.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - возвращает True если role == 'admin', иначе False
    
    @Invariants:
    - результат зависит только от self.role
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - логика проверки (role == 'admin')
    """
    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.role == self.Role.ADMIN
    # [END_IS_ADMIN_PROPERTY]
    
    # [START_IS_TRAINER_PROPERTY]
    """
    ANCHOR: IS_TRAINER_PROPERTY
    PURPOSE: Проверка является ли пользователь тренером.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - возвращает True если role == 'trainer', иначе False
    
    @Invariants:
    - результат зависит только от self.role
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - логика проверки (role == 'trainer')
    """
    @property
    def is_trainer(self):
        """Check if user is trainer."""
        return self.role == self.Role.TRAINER
    # [END_IS_TRAINER_PROPERTY]
    
    # [START_IS_LEARNER_PROPERTY]
    """
    ANCHOR: IS_LEARNER_PROPERTY
    PURPOSE: Проверка является ли пользователь слушателем.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - возвращает True если role == 'learner', иначе False
    
    @Invariants:
    - результат зависит только от self.role
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - логика проверки (role == 'learner')
    """
    @property
    def is_learner(self):
        """Check if user is learner."""
        return self.role == self.Role.LEARNER
    # [END_IS_LEARNER_PROPERTY]
# [END_USER_MODEL]


# === END_CHUNK: USER_MODEL_V1 ===


# === CHUNK: REFRESH_TOKEN_V1 [AUTHENTICATION] ===
# Описание: Модель для хранения refresh-токенов JWT аутентификации.
# Dependencies: USER_MODEL_V1
# [START_REFRESH_TOKEN_MODEL]
"""
ANCHOR: REFRESH_TOKEN_MODEL
PURPOSE: Модель для хранения refresh-токенов JWT аутентификации.

@PreConditions:
- нет нетривиальных предусловий для модели

@PostConditions:
- позволяет отзыв токенов и трекинг активных сессий

@Invariants:
- token всегда уникален
- один пользователь может иметь несколько активных токенов

@SideEffects:
- нет побочных эффектов на уровне класса

@ForbiddenChanges:
- связь с User через on_delete=CASCADE
"""
class RefreshToken(models.Model):
    """
    Model to store refresh tokens for JWT authentication.
    
    Allows token revocation and tracking of active sessions.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='refresh_tokens',
        verbose_name=_('Пользователь'),
    )
    token = models.CharField(_('Токен'), max_length=255, unique=True, db_index=True)
    expires_at = models.DateTimeField(_('Дата истечения'))
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    revoked_at = models.DateTimeField(_('Дата отзыва'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Refresh токен')
        verbose_name_plural = _('Refresh токены')
        ordering = ['-created_at']
    
    # [START_REFRESH_TOKEN_STR]
    """
    ANCHOR: REFRESH_TOKEN_STR
    PURPOSE: Строковое представление токена для отображения в админке.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - возвращает строку формата "email - токен[:20]..."
    
    @Invariants:
    - никогда не раскрывает полный токен
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - маскирование токена (только первые 20 символов)
    """
    def __str__(self):
        return f'{self.user.email} - {self.token[:20]}...'
    # [END_REFRESH_TOKEN_STR]
    
    # [START_IS_REVOKED_PROPERTY]
    """
    ANCHOR: IS_REVOKED_PROPERTY
    PURPOSE: Проверка отозван ли токен.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - возвращает True если revoked_at не None, иначе False
    
    @Invariants:
    - результат зависит только от self.revoked_at
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - логика проверки (revoked_at is not None)
    """
    @property
    def is_revoked(self):
        """Check if token is revoked."""
        return self.revoked_at is not None
    # [END_IS_REVOKED_PROPERTY]
    
    # [START_IS_EXPIRED_PROPERTY]
    """
    ANCHOR: IS_EXPIRED_PROPERTY
    PURPOSE: Проверка истёк ли срок действия токена.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - возвращает True если текущее время >= expires_at, иначе False
    
    @Invariants:
    - результат зависит только от self.expires_at и текущего времени
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - логика проверки (now >= expires_at)
    """
    @property
    def is_expired(self):
        """Check if token is expired."""
        return timezone.now() >= self.expires_at
    # [END_IS_EXPIRED_PROPERTY]
    
    # [START_REVOKE_TOKEN]
    """
    ANCHOR: REVOKE_TOKEN
    PURPOSE: Отзыв токена с фиксацией времени отзыва.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - revoked_at устанавливается в текущее время
    - изменения сохраняются в БД
    
    @Invariants:
    - только revoked_at изменяется
    
    @SideEffects:
    - обновление revoked_at в БД
    - логирование операции
    
    @ForbiddenChanges:
    - только update_fields=['revoked_at']
    """
    def revoke(self):
        """Revoke the token."""
        log_line("users", "DEBUG", "revoke", "REVOKE_TOKEN", "ENTRY", {
            "token_prefix": self.token[:10],
            "user_id": self.user_id,
        })
        
        self.revoked_at = timezone.now()
        self.save(update_fields=['revoked_at'])
        
        log_line("users", "INFO", "revoke", "REVOKE_TOKEN", "STATE_CHANGE", {
            "action": "token_revoked",
            "user_id": self.user_id,
        })
        log_line("users", "DEBUG", "revoke", "REVOKE_TOKEN", "EXIT", {
            "result": "success",
        })
    # [END_REVOKE_TOKEN]
# [END_REFRESH_TOKEN_MODEL]


# === END_CHUNK: REFRESH_TOKEN_V1 ===


# === CHUNK: PASSWORD_RESET_TOKEN_V1 [AUTHENTICATION] ===
# Описание: Модель для хранения токенов сброса пароля.
# Dependencies: USER_MODEL_V1
# [START_PASSWORD_RESET_TOKEN_MODEL]
"""
ANCHOR: PASSWORD_RESET_TOKEN_MODEL
PURPOSE: Модель для хранения токенов сброса пароля.

@PreConditions:
- нет нетривиальных предусловий для модели

@PostConditions:
- токены валидны ограниченное время
- токены могут использоваться только один раз

@Invariants:
- token всегда уникален
- один пользователь может иметь несколько токенов (но только один активный)

@SideEffects:
- нет побочных эффектов на уровне класса

@ForbiddenChanges:
- связь с User через on_delete=CASCADE
"""
class PasswordResetToken(models.Model):
    """
    Model to store password reset tokens.
    
    Tokens are valid for a limited time and can only be used once.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        verbose_name=_('Пользователь'),
    )
    token = models.CharField(_('Токен'), max_length=255, unique=True, db_index=True)
    expires_at = models.DateTimeField(_('Дата истечения'))
    used_at = models.DateTimeField(_('Дата использования'), null=True, blank=True)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Токен сброса пароля')
        verbose_name_plural = _('Токены сброса пароля')
        ordering = ['-created_at']
    
    # [START_PASSWORD_RESET_TOKEN_STR]
    """
    ANCHOR: PASSWORD_RESET_TOKEN_STR
    PURPOSE: Строковое представление токена для отображения в админке.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - возвращает строку формата "email - токен[:20]..."
    
    @Invariants:
    - никогда не раскрывает полный токен
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - маскирование токена (только первые 20 символов)
    """
    def __str__(self):
        return f'{self.user.email} - {self.token[:20]}...'
    # [END_PASSWORD_RESET_TOKEN_STR]
    
    # [START_IS_USED_PROPERTY]
    """
    ANCHOR: IS_USED_PROPERTY
    PURPOSE: Проверка использован ли токен.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - возвращает True если used_at не None, иначе False
    
    @Invariants:
    - результат зависит только от self.used_at
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - логика проверки (used_at is not None)
    """
    @property
    def is_used(self):
        """Check if token has been used."""
        return self.used_at is not None
    # [END_IS_USED_PROPERTY]
    
    # [START_PASSWORD_TOKEN_IS_EXPIRED]
    """
    ANCHOR: PASSWORD_TOKEN_IS_EXPIRED
    PURPOSE: Проверка истёк ли срок действия токена сброса пароля.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - возвращает True если текущее время >= expires_at, иначе False
    
    @Invariants:
    - результат зависит только от self.expires_at и текущего времени
    
    @SideEffects:
    - нет побочных эффектов
    
    @ForbiddenChanges:
    - логика проверки (now >= expires_at)
    """
    @property
    def is_expired(self):
        """Check if token is expired."""
        return timezone.now() >= self.expires_at
    # [END_PASSWORD_TOKEN_IS_EXPIRED]
    
    # [START_MARK_AS_USED]
    """
    ANCHOR: MARK_AS_USED
    PURPOSE: Пометить токен как использованный.
    
    @PreConditions:
    - нет нетривиальных предусловий
    
    @PostConditions:
    - used_at устанавливается в текущее время
    - изменения сохраняются в БД
    
    @Invariants:
    - только used_at изменяется
    
    @SideEffects:
    - обновление used_at в БД
    - логирование операции
    
    @ForbiddenChanges:
    - только update_fields=['used_at']
    """
    def mark_as_used(self):
        """Mark the token as used."""
        log_line("users", "DEBUG", "mark_as_used", "MARK_AS_USED", "ENTRY", {
            "token_prefix": self.token[:10],
            "user_id": self.user_id,
        })
        
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])
        
        log_line("users", "INFO", "mark_as_used", "MARK_AS_USED", "STATE_CHANGE", {
            "action": "token_used",
            "user_id": self.user_id,
        })
        log_line("users", "DEBUG", "mark_as_used", "MARK_AS_USED", "EXIT", {
            "result": "success",
        })
    # [END_MARK_AS_USED]
# [END_PASSWORD_RESET_TOKEN_MODEL]


# === END_CHUNK: PASSWORD_RESET_TOKEN_V1 ===