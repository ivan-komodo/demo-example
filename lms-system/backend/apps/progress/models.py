"""
Progress models for LMS System.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserProgress(models.Model):
    """
    Model for tracking user progress on modules.
    """
    
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', _('Не начато')
        IN_PROGRESS = 'in_progress', _('В процессе')
        COMPLETED = 'completed', _('Завершено')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name=_('Пользователь'),
    )
    module = models.ForeignKey(
        'courses.Module',
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name=_('Модуль'),
    )
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_STARTED,
    )
    completed_at = models.DateTimeField(_('Дата завершения'), null=True, blank=True)
    score = models.DecimalField(
        _('Результат'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    
    class Meta:
        verbose_name = _('Прогресс пользователя')
        verbose_name_plural = _('Прогресс пользователей')
        ordering = ['-completed_at']
        unique_together = ['user', 'module']
    
    def __str__(self):
        return f'{self.user.email} - {self.module.title} - {self.get_status_display()}'
    
    def mark_in_progress(self):
        """Mark module as in progress."""
        if self.status == self.Status.NOT_STARTED:
            self.status = self.Status.IN_PROGRESS
            self.save(update_fields=['status'])
    
    def mark_completed(self, score=None):
        """Mark module as completed."""
        from django.utils import timezone
        
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        if score is not None:
            self.score = score
        self.save()