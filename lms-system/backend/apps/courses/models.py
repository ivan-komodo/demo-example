"""
Course models for LMS System.

This module contains models for courses, modules, and course enrollments.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


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
    
    def __str__(self):
        return self.title
    
    @property
    def modules_count(self):
        """Return the number of modules in this course."""
        return self.modules.count()
    
    @property
    def enrolled_count(self):
        """Return the number of enrolled users."""
        return self.enrollments.filter(status='active').count()


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
    
    def __str__(self):
        return f'{self.course.title} - {self.title}'
    
    def save(self, *args, **kwargs):
        """Auto-set order_num if not provided."""
        if not self.order_num:
            max_order = Module.objects.filter(course=self.course).aggregate(
                max_order=models.Max('order_num')
            )['max_order']
            self.order_num = (max_order or 0) + 1
        super().save(*args, **kwargs)


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
    
    def __str__(self):
        return f'{self.user.email} - {self.course.title}'
    
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