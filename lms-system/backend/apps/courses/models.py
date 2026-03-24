"""
Course models for LMS System.

This module contains models for courses, modules, and course enrollments.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


# === CHUNK: COURSE_MODELS_V1 [COURSES] ===
# Описание: Модели для управления курсами, модулями и записями на курсы.
# Dependencies: USER_MODEL_V1, PROGRESS_MODELS_V1


# [START_COURSE_MODEL]
# ANCHOR: COURSE_MODEL
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет модель курса с полями title, description, status
# PURPOSE: Модель для хранения информации о курсах.
class Course(models.Model):
    """
    Model for courses.
    
    A course can have multiple modules and can be in draft, published, or archived state.
    """
    
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Черновик')
        PUBLISHED = 'published', _('Опубликован')
        ARCHIVED = 'archived', _('Архивирован')
    
    title = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('Курс')
        verbose_name_plural = _('Курсы')
        ordering = ['-created_at']
    
    # [START_COURSE_STR]
    # ANCHOR: COURSE_STR
    # @PreConditions:
    # - экземпляр Course существует
    # @PostConditions:
    # - возвращает строковое представление курса (title)
    # PURPOSE: Строковое представление курса для админки и отладки.
    def __str__(self):
        return self.title
    # [END_COURSE_STR]
    
    # [START_MODULES_COUNT]
    # ANCHOR: MODULES_COUNT
    # @PreConditions:
    # - экземпляр Course существует
    # @PostConditions:
    # - возвращает количество модулей в курсе
    # PURPOSE: Получение количества модулей в курсе.
    @property
    def modules_count(self):
        """Return the number of modules in this course."""
        return self.modules.count()
    # [END_MODULES_COUNT]
    
    # [START_ENROLLED_COUNT]
    # ANCHOR: ENROLLED_COUNT
    # @PreConditions:
    # - экземпляр Course существует
    # @PostConditions:
    # - возвращает количество активных записей на курс
    # PURPOSE: Получение количества активных записей на курс.
    @property
    def enrolled_count(self):
        """Return the number of enrolled users."""
        return self.enrollments.filter(status='active').count()
    # [END_ENROLLED_COUNT]


# [END_COURSE_MODEL]


# [START_MODULE_MODEL]
# ANCHOR: MODULE_MODEL
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет модель модуля с полями course, title, content_type, order_num
# PURPOSE: Модель для хранения модулей курса с контентом.
class Module(models.Model):
    """
    Model for course modules.
    
    A module belongs to a course and can contain text, PDF, or video content.
    """
    
    class ContentType(models.TextChoices):
        TEXT = 'text', _('Текст')
        PDF = 'pdf', _('PDF')
        VIDEO = 'video', _('Видео')
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name=_('Курс'),
    )
    title = models.CharField(_('Название'), max_length=255)
    content_type = models.CharField(
        _('Тип контента'),
        max_length=20,
        choices=ContentType.choices,
        default=ContentType.TEXT,
    )
    content_text = models.TextField(_('Текст контента'), blank=True)
    content_url = models.URLField(_('URL контента'), blank=True, null=True)
    content_file = models.FileField(
        _('Файл контента'),
        upload_to='modules/files/',
        blank=True,
        null=True,
    )
    order_num = models.PositiveIntegerField(_('Порядковый номер'), default=0)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('Модуль')
        verbose_name_plural = _('Модули')
        ordering = ['order_num', 'created_at']
    
    # [START_MODULE_STR]
    # ANCHOR: MODULE_STR
    # @PreConditions:
    # - экземпляр Module существует
    # @PostConditions:
    # - возвращает строку вида "Название курса - Название модуля"
    # PURPOSE: Строковое представление модуля для админки и отладки.
    def __str__(self):
        return f'{self.course.title} - {self.title}'
    # [END_MODULE_STR]
    
    # [START_MODULE_SAVE]
    # ANCHOR: MODULE_SAVE
    # @PreConditions:
    # - экземпляр Module инициализирован
    # @PostConditions:
    # - при отсутствии order_num устанавливается следующий по порядку номер
    # - экземпляр сохранён в БД
    # PURPOSE: Автоматическая установка порядкового номера модуля при создании.
    def save(self, *args, **kwargs):
        """Auto-set order_num if not provided."""
        if not self.order_num:
            max_order = Module.objects.filter(course=self.course).aggregate(
                max_order=models.Max('order_num')
            )['max_order']
            self.order_num = (max_order or 0) + 1
        super().save(*args, **kwargs)
    # [END_MODULE_SAVE]


# [END_MODULE_MODEL]


# [START_COURSE_ENROLLMENT_MODEL]
# ANCHOR: COURSE_ENROLLMENT_MODEL
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет модель записи на курс с полями user, course, status
# PURPOSE: Модель для отслеживания записей пользователей на курсы.
class CourseEnrollment(models.Model):
    """
    Model for course enrollments.
    
    Tracks user enrollment in courses with status and completion date.
    """
    
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Активна')
        COMPLETED = 'completed', _('Завершена')
        DROPPED = 'dropped', _('Прервана')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('Пользователь'),
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('Курс'),
    )
    enrolled_at = models.DateTimeField(_('Дата записи'), auto_now_add=True)
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    completed_at = models.DateTimeField(_('Дата завершения'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Запись на курс')
        verbose_name_plural = _('Записи на курсы')
        ordering = ['-enrolled_at']
        unique_together = ['user', 'course']
    
    # [START_ENROLLMENT_STR]
    # ANCHOR: ENROLLMENT_STR
    # @PreConditions:
    # - экземпляр CourseEnrollment существует
    # @PostConditions:
    # - возвращает строку вида "email пользователя - название курса"
    # PURPOSE: Строковое представление записи для админки и отладки.
    def __str__(self):
        return f'{self.user.email} - {self.course.title}'
    # [END_ENROLLMENT_STR]
    
    # [START_PROGRESS_PERCENTAGE]
    # ANCHOR: PROGRESS_PERCENTAGE
    # @PreConditions:
    # - экземпляр CourseEnrollment существует
    # @PostConditions:
    # - возвращает процент завершения курса (0-100)
    # PURPOSE: Расчёт процента прогресса по курсу для данной записи.
    @property
    def progress_percentage(self):
        """Calculate progress percentage for this enrollment."""
        total_modules = self.course.modules.count()
        if total_modules == 0:
            return 0
        
        # Import here to avoid circular imports
        from apps.progress.models import UserProgress
        
        completed_modules = UserProgress.objects.filter(
            user=self.user,
            module__course=self.course,
            status='completed',
        ).count()
        
        return round((completed_modules / total_modules) * 100, 2)
    # [END_PROGRESS_PERCENTAGE]


# [END_COURSE_ENROLLMENT_MODEL]


# === END_CHUNK: COURSE_MODELS_V1 ===