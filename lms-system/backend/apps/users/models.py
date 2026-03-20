"""
User models for LMS System.

This module contains the custom User model and related models
for authentication and user management.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for User model."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError(_('Email обязателен'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
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
    
    def get_by_natural_key(self, email):
        """Get user by natural key (email)."""
        return self.get(email=email)


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
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name of the user."""
        return self.full_name or self.email
    
    def get_short_name(self):
        """Return the short name of the user."""
        return self.email.split('@')[0]
    
    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.role == self.Role.ADMIN
    
    @property
    def is_trainer(self):
        """Check if user is trainer."""
        return self.role == self.Role.TRAINER
    
    @property
    def is_learner(self):
        """Check if user is learner."""
        return self.role == self.Role.LEARNER


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
    
    def __str__(self):
        return f'{self.user.email} - {self.token[:20]}...'
    
    @property
    def is_revoked(self):
        """Check if token is revoked."""
        return self.revoked_at is not None
    
    @property
    def is_expired(self):
        """Check if token is expired."""
        return timezone.now() >= self.expires_at
    
    def revoke(self):
        """Revoke the token."""
        self.revoked_at = timezone.now()
        self.save(update_fields=['revoked_at'])


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
    
    def __str__(self):
        return f'{self.user.email} - {self.token[:20]}...'
    
    @property
    def is_used(self):
        """Check if token has been used."""
        return self.used_at is not None
    
    @property
    def is_expired(self):
        """Check if token is expired."""
        return timezone.now() >= self.expires_at
    
    def mark_as_used(self):
        """Mark the token as used."""
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])