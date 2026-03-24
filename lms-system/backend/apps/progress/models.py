"""
Progress models for LMS System.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


# === CHUNK: PROGRESS_MODELS_V1 [PROGRESS] ===
# Описание: Модель для отслеживания прогресса пользователя по модулям.
# Dependencies: COURSE_MODELS_V1


# [START_USER_PROGRESS_MODEL]
# ANCHOR: USER_PROGRESS_MODEL
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт модель UserProgress с полями user, module, status, completed_at, score
# PURPOSE: Модель для отслеживания прогресса пользователя по модулям.
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
    
    # [START_USER_PROGRESS_STR]
    # ANCHOR: USER_PROGRESS_STR
    # @PreConditions:
    # - экземпляр UserProgress существует
    # @PostConditions:
    # - возвращает строковое представление прогресса
    # PURPOSE: Строковое представление прогресса пользователя.
    def __str__(self):
        return f'{self.user.email} - {self.module.title} - {self.get_status_display()}'
    # [END_USER_PROGRESS_STR]
    
    # [START_MARK_IN_PROGRESS]
    # ANCHOR: MARK_IN_PROGRESS
    # @PreConditions:
    # - экземпляр UserProgress существует
    # @PostConditions:
    # - если статус NOT_STARTED, меняет на IN_PROGRESS
    # - сохраняет изменения в БД
    # PURPOSE: Отметить модуль как "в процессе" изучения.
    def mark_in_progress(self):
        """Mark module as in progress."""
        if self.status == self.Status.NOT_STARTED:
            self.status = self.Status.IN_PROGRESS
            self.save(update_fields=['status'])
    # [END_MARK_IN_PROGRESS]
    
    # [START_MARK_COMPLETED]
    # ANCHOR: MARK_COMPLETED
    # @PreConditions:
    # - экземпляр UserProgress существует
    # @PostConditions:
    # - статус меняется на COMPLETED
    # - completed_at устанавливается в текущее время
    # - при наличии score сохраняется результат
    # PURPOSE: Отметить модуль как завершённый.
    def mark_completed(self, score=None):
        """Mark module as completed."""
        from django.utils import timezone
        
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        if score is not None:
            self.score = score
        self.save()
    # [END_MARK_COMPLETED]


# [END_USER_PROGRESS_MODEL]


# === END_CHUNK: PROGRESS_MODELS_V1 ===