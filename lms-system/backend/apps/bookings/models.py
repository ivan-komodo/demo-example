"""
Booking models for LMS System.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


# === CHUNK: BOOKING_MODELS_V1 [BOOKINGS] ===
# Описание: Модели для бронирования ресурсов (аудитории, тренеры, оборудование).
# Dependencies: none


# [START_RESOURCE_MODEL]
# ANCHOR: RESOURCE_MODEL
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт модель ресурса с полями name, type, description, capacity, is_active
# PURPOSE: Модель для бронирования ресурсов (аудитории, тренеры, оборудование).
class Resource(models.Model):
    """
    Model for bookable resources (classrooms, trainers, equipment).
    """
    
    class Type(models.TextChoices):
        CLASSROOM = 'classroom', _('Аудитория')
        TRAINER = 'trainer', _('Тренер')
        EQUIPMENT = 'equipment', _('Оборудование')
    
    name = models.CharField(_('Название'), max_length=255)
    type = models.CharField(
        _('Тип'),
        max_length=50,
        choices=Type.choices,
        default=Type.CLASSROOM,
    )
    description = models.TextField(_('Описание'), blank=True)
    capacity = models.PositiveIntegerField(_('Вместимость'), null=True, blank=True)
    is_active = models.BooleanField(_('Активен'), default=True)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Ресурс')
        verbose_name_plural = _('Ресурсы')
        ordering = ['name']
    
    # [START_RESOURCE_STR]
    # ANCHOR: RESOURCE_STR
    # @PreConditions:
    # - экземпляр модели существует
    # @PostConditions:
    # - возвращает строковое представление ресурса
    # PURPOSE: Строковое представление ресурса для админки и логов.
    def __str__(self):
        return f'{self.name} ({self.get_type_display()})'
    # [END_RESOURCE_STR]


# [END_RESOURCE_MODEL]


# [START_BOOKING_MODEL]
# ANCHOR: BOOKING_MODEL
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт модель бронирования с полями resource, user, course, title, start_time, end_time, status
# PURPOSE: Модель для бронирования ресурсов пользователями.
class Booking(models.Model):
    """
    Model for resource bookings.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Ожидает')
        CONFIRMED = 'confirmed', _('Подтверждено')
        CANCELLED = 'cancelled', _('Отменено')
    
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('Ресурс'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('Пользователь'),
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        verbose_name=_('Курс'),
    )
    title = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)
    start_time = models.DateTimeField(_('Время начала'))
    end_time = models.DateTimeField(_('Время окончания'))
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('Бронирование')
        verbose_name_plural = _('Бронирования')
        ordering = ['-start_time']
    
    # [START_BOOKING_STR]
    # ANCHOR: BOOKING_STR
    # @PreConditions:
    # - экземпляр модели существует
    # @PostConditions:
    # - возвращает строковое представление бронирования
    # PURPOSE: Строковое представление бронирования для админки и логов.
    def __str__(self):
        return f'{self.title} - {self.resource.name} ({self.start_time})'
    # [END_BOOKING_STR]
    
    # [START_BOOKING_CLEAN]
    # ANCHOR: BOOKING_CLEAN
    # @PreConditions:
    # - экземпляр модели существует
    # @PostConditions:
    # - при ошибке выбрасывает ValidationError
    # PURPOSE: Валидация времени бронирования (end_time > start_time).
    def clean(self):
        """Validate booking times."""
        from django.core.exceptions import ValidationError
        
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({
                'end_time': _('Время окончания должно быть позже времени начала.')
            })
    # [END_BOOKING_CLEAN]
    
    # [START_CHECK_CONFLICT]
    # ANCHOR: CHECK_CONFLICT
    # @PreConditions:
    # - экземпляр модели существует
    # - resource, start_time, end_time заданы
    # @PostConditions:
    # - возвращает True если есть конфликт, иначе False
    # PURPOSE: Проверка конфликтов бронирования ресурса.
    def check_conflict(self):
        """Check for booking conflicts."""
        conflicting = Booking.objects.filter(
            resource=self.resource,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        ).exclude(pk=self.pk)
        
        return conflicting.exists()
    # [END_CHECK_CONFLICT]


# [END_BOOKING_MODEL]


# === END_CHUNK: BOOKING_MODELS_V1 ===