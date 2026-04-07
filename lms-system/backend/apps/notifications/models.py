"""
Notification models for LMS System.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils import log_line


# === CHUNK: NOTIFICATION_MODELS_V1 [NOTIFICATIONS] ===
# Описание: Модель уведомлений пользователей.
# Dependencies: CORE_UTILS_V1


# [START_NOTIFICATION_MODEL]
"""
ANCHOR: NOTIFICATION_MODEL
PURPOSE: Модель для хранения уведомлений пользователей.

@PreConditions:
- нет нетривиальных предусловий

@PostConditions:
- создаёт модель уведомления с полями user, type, title, message, is_read
- обеспечивает автоматическую сортировку по created_at DESC

@Invariants:
- is_read всегда boolean значение
- type всегда один из допустимых Type choices
- created_at не изменяется после создания

@SideEffects:
- создание записи в БД при сохранении

@ForbiddenChanges:
- поле created_at (auto_now_add)
- ordering в Meta (сортировка по умолчанию)
"""
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
    
    # [START_NOTIFICATION_STR]
    """
    ANCHOR: NOTIFICATION_STR
    PURPOSE: Строковое представление уведомления для админки и логов.

    @PreConditions:
    - экземпляр модели существует
    - user связан с User объектом

    @PostConditions:
    - возвращает строку формата "{user.email} - {title}"

    @Invariants:
    - всегда возвращает строку

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - формат вывода (email - title)
    """
    def __str__(self):
        log_line(
            "notifications",
            "DEBUG",
            "__str__",
            "NOTIFICATION_STR",
            "ENTRY",
            {"id": self.id, "title": self.title[:50] if self.title else None}
        )
        result = f'{self.user.email} - {self.title}'
        log_line(
            "notifications",
            "DEBUG",
            "__str__",
            "NOTIFICATION_STR",
            "EXIT",
            {"result": result[:100]}
        )
        return result
    # [END_NOTIFICATION_STR]
    
    # [START_MARK_AS_READ]
    """
    ANCHOR: MARK_AS_READ
    PURPOSE: Пометить уведомление как прочитанное.

    @PreConditions:
    - экземпляр модели существует

    @PostConditions:
    - устанавливает is_read=True и сохраняет в БД
    - если уже прочитано - не выполняет save()

    @Invariants:
    - id уведомления не изменяется

    @SideEffects:
- запись в БД (только если is_read был False)

    @ForbiddenChanges:
    - только поле is_read обновляется
    - сохранение только при is_read=False (оптимизация)
    """
    def mark_as_read(self):
        log_line(
            "notifications",
            "DEBUG",
            "mark_as_read",
            "MARK_AS_READ",
            "ENTRY",
            {"id": self.id, "is_read": self.is_read}
        )
        
        if not self.is_read:
            log_line(
                "notifications",
                "DEBUG",
                "mark_as_read",
                "MARK_AS_READ",
                "BRANCH",
                {"branch": "will_mark_read", "current_is_read": False}
            )
            self.is_read = True
            self.save(update_fields=['is_read'])
            log_line(
                "notifications",
                "INFO",
                "mark_as_read",
                "MARK_AS_READ",
                "STATE_CHANGE",
                {"entity": "notification", "id": self.id, "from": "unread", "to": "read"}
            )
        else:
            log_line(
                "notifications",
                "DEBUG",
                "mark_as_read",
                "MARK_AS_READ",
                "BRANCH",
                {"branch": "already_read", "current_is_read": True}
            )
        
        log_line(
            "notifications",
            "DEBUG",
            "mark_as_read",
            "MARK_AS_READ",
            "EXIT",
            {"id": self.id, "is_read": self.is_read}
        )
    # [END_MARK_AS_READ]


# [END_NOTIFICATION_MODEL]


# === END_CHUNK: NOTIFICATION_MODELS_V1 ===
