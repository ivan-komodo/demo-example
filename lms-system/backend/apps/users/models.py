"""
User models for LMS System.

This module contains the custom User model and related models
for authentication and user management.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# === CHUNK: USER_MANAGER_V1 [AUTHENTICATION] ===
# Описание: Менеджер для создания пользователей и суперпользователей.
# Dependencies: none
class UserManager(BaseUserManager):
    """Custom user manager for User model."""
    
    # [START_CREATE_USER]
    # ANCHOR: CREATE_USER
    # @PreConditions:
    # - email: непустая строка с валидным email-форматом
    # - password: строка (может быть None для пользователя без пароля)
    # @PostConditions:
    # - возвращает созданный экземпляр User с нормализованным email
    # - при отсутствии email выбрасывает ValueError
    # PURPOSE: Создание обычного пользователя с указанным email и паролем.
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError(_('Email обязателен'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    # [END_CREATE_USER]
    
    # [START_CREATE_SUPERUSER]
    # ANCHOR: CREATE_SUPERUSER
    # @PreConditions:
    # - email: непустая строка с валидным email-форматом
    # - password: непустая строка
    # - extra_fields: опциональные поля (is_staff, is_superuser, is_active, role)
    # @PostConditions:
    # - возвращает созданный экземпляр User с is_staff=True, is_superuser=True
    # - при некорректных флагах выбрасывает ValueError
    # PURPOSE: Создание суперпользователя с полными правами доступа.
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)
    # [END_CREATE_SUPERUSER]
    
    # [START_GET_BY_NATURAL_KEY]
    # ANCHOR: GET_BY_NATURAL_KEY
    # @PreConditions:
    # - email: строка для поиска пользователя
    # @PostConditions:
    # - возвращает экземпляр User с указанным email
    # - при отсутствии пользователя выбрасывает DoesNotExist
    # PURPOSE: Получение пользователя по естественному ключу (email).
    def get_by_natural_key(self, email):
        """Get user by natural key (email)."""
        return self.get(email=email)
    # [END_GET_BY_NATURAL_KEY]


# === END_CHUNK: USER_MANAGER_V1 ===


# === CHUNK: USER_MODEL_V1 [AUTHENTICATION] ===
# Описание: Основная модель пользователя системы с ролями admin/trainer/learner.
# Dependencies: USER_MANAGER_V1
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
    # ANCHOR: USER_STR
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает строковое представление пользователя (email)
    # PURPOSE: Строковое представление пользователя для отображения в админке и логах.
    def __str__(self):
        return self.email
    # [END_USER_STR]
    
    # [START_GET_FULL_NAME]
    # ANCHOR: GET_FULL_NAME
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает full_name если заполнено, иначе email
    # PURPOSE: Получение полного имени пользователя или email как fallback.
    def get_full_name(self):
        """Return the full name of the user."""
        return self.full_name or self.email
    # [END_GET_FULL_NAME]
    
    # [START_GET_SHORT_NAME]
    # ANCHOR: GET_SHORT_NAME
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает часть email до символа @
    # PURPOSE: Получение короткого имени пользователя для отображения.
    def get_short_name(self):
        """Return the short name of the user."""
        return self.email.split('@')[0]
    # [END_GET_SHORT_NAME]
    
    # [START_IS_ADMIN_PROPERTY]
    # ANCHOR: IS_ADMIN_PROPERTY
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает True если role == 'admin', иначе False
    # PURPOSE: Проверка является ли пользователь администратором.
    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.role == self.Role.ADMIN
    # [END_IS_ADMIN_PROPERTY]
    
    # [START_IS_TRAINER_PROPERTY]
    # ANCHOR: IS_TRAINER_PROPERTY
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает True если role == 'trainer', иначе False
    # PURPOSE: Проверка является ли пользователь тренером.
    @property
    def is_trainer(self):
        """Check if user is trainer."""
        return self.role == self.Role.TRAINER
    # [END_IS_TRAINER_PROPERTY]
    
    # [START_IS_LEARNER_PROPERTY]
    # ANCHOR: IS_LEARNER_PROPERTY
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает True если role == 'learner', иначе False
    # PURPOSE: Проверка является ли пользователь слушателем.
    @property
    def is_learner(self):
        """Check if user is learner."""
        return self.role == self.Role.LEARNER
    # [END_IS_LEARNER_PROPERTY]


# === END_CHUNK: USER_MODEL_V1 ===


# === CHUNK: REFRESH_TOKEN_V1 [AUTHENTICATION] ===
# Описание: Модель для хранения refresh-токенов JWT аутентификации.
# Dependencies: USER_MODEL_V1
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
    # ANCHOR: REFRESH_TOKEN_STR
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает строку формата "email - токен[:20]..."
    # PURPOSE: Строковое представление токена для отображения в админке.
    def __str__(self):
        return f'{self.user.email} - {self.token[:20]}...'
    # [END_REFRESH_TOKEN_STR]
    
    # [START_IS_REVOKED_PROPERTY]
    # ANCHOR: IS_REVOKED_PROPERTY
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает True если revoked_at не None, иначе False
    # PURPOSE: Проверка отозван ли токен.
    @property
    def is_revoked(self):
        """Check if token is revoked."""
        return self.revoked_at is not None
    # [END_IS_REVOKED_PROPERTY]
    
    # [START_IS_EXPIRED_PROPERTY]
    # ANCHOR: IS_EXPIRED_PROPERTY
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает True если текущее время >= expires_at, иначе False
    # PURPOSE: Проверка истёк ли срок действия токена.
    @property
    def is_expired(self):
        """Check if token is expired."""
        return timezone.now() >= self.expires_at
    # [END_IS_EXPIRED_PROPERTY]
    
    # [START_REVOKE_TOKEN]
    # ANCHOR: REVOKE_TOKEN
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - revoked_at устанавливается в текущее время
    # - изменения сохраняются в БД
    # PURPOSE: Отзыв токена с фиксацией времени отзыва.
    def revoke(self):
        """Revoke the token."""
        self.revoked_at = timezone.now()
        self.save(update_fields=['revoked_at'])
    # [END_REVOKE_TOKEN]


# === END_CHUNK: REFRESH_TOKEN_V1 ===


# === CHUNK: PASSWORD_RESET_TOKEN_V1 [AUTHENTICATION] ===
# Описание: Модель для хранения токенов сброса пароля.
# Dependencies: USER_MODEL_V1
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
    # ANCHOR: PASSWORD_RESET_TOKEN_STR
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает строку формата "email - токен[:20]..."
    # PURPOSE: Строковое представление токена для отображения в админке.
    def __str__(self):
        return f'{self.user.email} - {self.token[:20]}...'
    # [END_PASSWORD_RESET_TOKEN_STR]
    
    # [START_IS_USED_PROPERTY]
    # ANCHOR: IS_USED_PROPERTY
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает True если used_at не None, иначе False
    # PURPOSE: Проверка использован ли токен.
    @property
    def is_used(self):
        """Check if token has been used."""
        return self.used_at is not None
    # [END_IS_USED_PROPERTY]
    
    # [START_PASSWORD_TOKEN_IS_EXPIRED]
    # ANCHOR: PASSWORD_TOKEN_IS_EXPIRED
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает True если текущее время >= expires_at, иначе False
    # PURPOSE: Проверка истёк ли срок действия токена сброса пароля.
    @property
    def is_expired(self):
        """Check if token is expired."""
        return timezone.now() >= self.expires_at
    # [END_PASSWORD_TOKEN_IS_EXPIRED]
    
    # [START_MARK_AS_USED]
    # ANCHOR: MARK_AS_USED
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - used_at устанавливается в текущее время
    # - изменения сохраняются в БД
    # PURPOSE: Пометить токен как использованный.
    def mark_as_used(self):
        """Mark the token as used."""
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])
    # [END_MARK_AS_USED]


# === END_CHUNK: PASSWORD_RESET_TOKEN_V1 ===