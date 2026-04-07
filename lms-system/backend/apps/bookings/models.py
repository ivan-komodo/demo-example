"""
Booking models for LMS System.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils import log_line


# === CHUNK: BOOKING_MODELS_V1 [BOOKINGS] ===
# Описание: Модели для бронирования ресурсов (аудитории, тренеры, оборудование).
# Dependencies: none


# [START_RESOURCE_MODEL]
"""
ANCHOR: RESOURCE_MODEL
PURPOSE: Модель для бронирования ресурсов (аудитории, тренеры, оборудование).

@PreConditions:
- нет нетривиальных предусловий

@PostConditions:
- создаёт модель ресурса с полями name, type, description, capacity, is_active
- предоставляет метод __str__ для строкового представления

@Invariants:
- type всегда один из: classroom, trainer, equipment
- is_active по умолчанию True

@SideEffects:
- создание таблицы resources в БД при миграции

@ForbiddenChanges:
- значения Type.choices (типы ресурсов)
- поле is_active (используется для soft delete)
"""
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
    """
    ANCHOR: RESOURCE_STR
    PURPOSE: Строковое представление ресурса для админки и логов.

    @PreConditions:
    - экземпляр модели существует

    @PostConditions:
    - возвращает строку формата "name (type_display)"

    @Invariants:
    - всегда возвращает непустую строку

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - формат вывода (имя + тип в скобках)
    """
    def __str__(self):
        log_line("bookings", "DEBUG", "Resource.__str__", "RESOURCE_STR", "ENTRY", {
            "resource_id": self.pk,
            "name": self.name,
            "type": self.type,
        })
        result = f'{self.name} ({self.get_type_display()})'
        log_line("bookings", "DEBUG", "Resource.__str__", "RESOURCE_STR", "EXIT", {
            "result": result,
        })
        return result
    # [END_RESOURCE_STR]


# [END_RESOURCE_MODEL]


# [START_BOOKING_MODEL]
"""
ANCHOR: BOOKING_MODEL
PURPOSE: Модель для бронирования ресурсов пользователями.

@PreConditions:
- нет нетривиальных предусловий

@PostConditions:
- создаёт модель бронирования с полями resource, user, course, title, start_time, end_time, status
- предоставляет методы для валидации и проверки конфликтов

@Invariants:
- status всегда один из: pending, confirmed, cancelled
- start_time всегда меньше end_time (проверяется в clean)
- created_at и updated_at автоматически управляются Django

@SideEffects:
- создание таблицы bookings в БД при миграции
- внешние ключи к Resource, User, Course

@ForbiddenChanges:
- значения Status.choices (статусы бронирования)
- поля start_time, end_time (критичны для логики конфликтов)
"""
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
    """
    ANCHOR: BOOKING_STR
    PURPOSE: Строковое представление бронирования для админки и логов.

    @PreConditions:
    - экземпляр модели существует
    - resource связан с бронированием

    @PostConditions:
    - возвращает строку формата "title - resource.name (start_time)"

    @Invariants:
    - всегда возвращает непустую строку

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - формат вывода (title - resource - time)
    """
    def __str__(self):
        log_line("bookings", "DEBUG", "Booking.__str__", "BOOKING_STR", "ENTRY", {
            "booking_id": self.pk,
            "title": self.title,
            "resource_id": self.resource_id,
        })
        result = f'{self.title} - {self.resource.name} ({self.start_time})'
        log_line("bookings", "DEBUG", "Booking.__str__", "BOOKING_STR", "EXIT", {
            "result": result,
        })
        return result
    # [END_BOOKING_STR]
    
    # [START_BOOKING_CLEAN]
    """
    ANCHOR: BOOKING_CLEAN
    PURPOSE: Валидация времени бронирования (end_time > start_time).

    @PreConditions:
    - экземпляр модели существует
    - start_time и end_time заданы (могут быть None)

    @PostConditions:
    - при start_time >= end_time выбрасывает ValidationError
    - при корректных временах завершается без ошибок

    @Invariants:
    - никогда не изменяет состояние модели
    - проверка выполняется только на уровне Django (не БД)

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - условие валидации (start_time < end_time)
    """
    def clean(self):
        """Validate booking times."""
        from django.core.exceptions import ValidationError
        
        log_line("bookings", "DEBUG", "Booking.clean", "BOOKING_CLEAN", "ENTRY", {
            "booking_id": self.pk,
            "start_time": str(self.start_time) if self.start_time else None,
            "end_time": str(self.end_time) if self.end_time else None,
        })
        
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            log_line("bookings", "WARN", "Booking.clean", "BOOKING_CLEAN", "ERROR", {
                "reason": "invalid_time_range",
                "start_time": str(self.start_time),
                "end_time": str(self.end_time),
            })
            log_line("bookings", "DEBUG", "Booking.clean", "BOOKING_CLEAN", "EXIT", {
                "result": "validation_error",
            })
            raise ValidationError({
                'end_time': _('Время окончания должно быть позже времени начала.')
            })
        
        log_line("bookings", "DEBUG", "Booking.clean", "BOOKING_CLEAN", "EXIT", {
            "result": "valid",
        })
    # [END_BOOKING_CLEAN]
    
    # [START_CHECK_CONFLICT]
    """
    ANCHOR: CHECK_CONFLICT
    PURPOSE: Проверка конфликтов бронирования ресурса.

    @PreConditions:
    - экземпляр модели существует
    - resource, start_time, end_time заданы

    @PostConditions:
    - возвращает True если есть конфликт с другими бронированиями
    - возвращает False если слот свободен
    - конфликт определяется пересечением временных интервалов

    @Invariants:
    - не изменяет состояние базы данных
    - проверяет только PENDING и CONFIRMED статусы
    - исключает текущее бронирование из проверки (по pk)

    @SideEffects:
    - нет побочных эффектов (только чтение БД)

    @ForbiddenChanges:
    - логика пересечения интервалов (start_time < other.end_time AND end_time > other.start_time)
    - проверяемые статусы (PENDING, CONFIRMED)
    """
    def check_conflict(self):
        """Check for booking conflicts."""
        log_line("bookings", "DEBUG", "Booking.check_conflict", "CHECK_CONFLICT", "ENTRY", {
            "booking_id": self.pk,
            "resource_id": self.resource_id,
            "start_time": str(self.start_time),
            "end_time": str(self.end_time),
        })
        
        conflicting = Booking.objects.filter(
            resource=self.resource,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        ).exclude(pk=self.pk)
        
        has_conflict = conflicting.exists()
        
        log_line("bookings", "DEBUG", "Booking.check_conflict", "CHECK_CONFLICT", "CHECK", {
            "check": "conflict_exists",
            "result": has_conflict,
            "resource_id": self.resource_id,
        })
        
        log_line("bookings", "DEBUG", "Booking.check_conflict", "CHECK_CONFLICT", "EXIT", {
            "result": "conflict" if has_conflict else "available",
        })
        return has_conflict
    # [END_CHECK_CONFLICT]


# [END_BOOKING_MODEL]


# === END_CHUNK: BOOKING_MODELS_V1 ===
