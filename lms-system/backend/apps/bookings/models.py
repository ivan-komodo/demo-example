"""
Booking models for LMS System.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


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
    
    def __str__(self):
        return f'{self.name} ({self.get_type_display()})'


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
    
    def __str__(self):
        return f'{self.title} - {self.resource.name} ({self.start_time})'
    
    def clean(self):
        """Validate booking times."""
        from django.core.exceptions import ValidationError
        
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({
                'end_time': _('Время окончания должно быть позже времени начала.')
            })
    
    def check_conflict(self):
        """Check for booking conflicts."""
        conflicting = Booking.objects.filter(
            resource=self.resource,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        ).exclude(pk=self.pk)
        
        return conflicting.exists()