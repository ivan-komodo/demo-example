"""
Notification models for LMS System.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """
    Model for user notifications.
    """
    
    class Type(models.TextChoices):
        INFO = 'info', _('Информация')
        WARNING = 'warning', _('Предупреждение')
        SUCCESS = 'success', _('Успех')
        ERROR = 'error', _('Ошибка')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Пользователь'),
    )
    type = models.CharField(
        _('Тип'),
        max_length=50,
        choices=Type.choices,
        default=Type.INFO,
    )
    title = models.CharField(_('Заголовок'), max_length=255)
    message = models.TextField(_('Сообщение'))
    is_read = models.BooleanField(_('Прочитано'), default=False)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Уведомление')
        verbose_name_plural = _('Уведомления')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.email} - {self.title}'
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])