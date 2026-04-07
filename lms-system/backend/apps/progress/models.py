"""
Progress models for LMS System.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils import log_line


# === CHUNK: PROGRESS_MODELS_V1 [PROGRESS] ===
# Описание: Модель для отслеживания прогресса пользователя по модулям.
# Dependencies: COURSE_MODELS_V1


# [START_USER_PROGRESS_MODEL]
"""
ANCHOR: USER_PROGRESS_MODEL
PURPOSE: Модель для отслеживания прогресса пользователя по модулям.

@PreConditions:
- нет нетривиальных предусловий для объявления модели

@PostConditions:
- создаёт модель UserProgress с полями user, module, status, completed_at, score
- обеспечивает unique_together для (user, module)

@Invariants:
- каждый пользователь имеет не более одной записи прогресса на модуль

@SideEffects:
- создание таблицы в БД при миграции

@ForbiddenChanges:
- unique_together = ['user', 'module'] (гарантия уникальности)
- Status choices (статусы прогресса)
"""
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
    """
    ANCHOR: USER_PROGRESS_STR
    PURPOSE: Строковое представление прогресса пользователя для отображения.

    @PreConditions:
    - экземпляр UserProgress существует
    - self.user.email доступен
    - self.module.title доступен

    @PostConditions:
    - возвращает строку формата "email - title - status_display"

    @Invariants:
    - всегда возвращает непустую строку

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - формат строкового представления
    """
    def __str__(self):
        log_line("progress", "DEBUG", "__str__", "USER_PROGRESS_STR", "ENTRY", {
            "progress_id": self.id,
        })
        result = f'{self.user.email} - {self.module.title} - {self.get_status_display()}'
        log_line("progress", "DEBUG", "__str__", "USER_PROGRESS_STR", "EXIT", {
            "result": result[:50],
        })
        return result
    # [END_USER_PROGRESS_STR]
    
    # [START_MARK_IN_PROGRESS]
    """
    ANCHOR: MARK_IN_PROGRESS
    PURPOSE: Отметить модуль как "в процессе" изучения.

    @PreConditions:
    - экземпляр UserProgress существует
    - current status is NOT_STARTED

    @PostConditions:
    - если статус был NOT_STARTED, меняется на IN_PROGRESS
    - изменения сохраняются в БД
    - если статус не NOT_STARTED, изменений нет

    @Invariants:
    - ID записи не меняется
    - user и module не меняются

    @SideEffects:
    - запись в БД (_save)_

    @ForbiddenChanges:
    - проверка только для NOT_STARTED (не менять status если уже IN_PROGRESS/COMPLETED)
    """
    def mark_in_progress(self):
        log_line("progress", "DEBUG", "mark_in_progress", "MARK_IN_PROGRESS", "ENTRY", {
            "progress_id": self.id,
            "current_status": self.status,
        })
        
        if self.status == self.Status.NOT_STARTED:
            log_line("progress", "DEBUG", "mark_in_progress", "MARK_IN_PROGRESS", "BRANCH", {
                "branch": "status_is_not_started",
                "will_change_to": self.Status.IN_PROGRESS,
            })
            self.status = self.Status.IN_PROGRESS
            self.save(update_fields=['status'])
            log_line("progress", "INFO", "mark_in_progress", "MARK_IN_PROGRESS", "STATE_CHANGE", {
                "entity": "progress",
                "id": self.id,
                "from": "not_started",
                "to": "in_progress",
            })
        else:
            log_line("progress", "DEBUG", "mark_in_progress", "MARK_IN_PROGRESS", "BRANCH", {
                "branch": "status_not_not_started",
                "no_change": True,
            })
        
        log_line("progress", "DEBUG", "mark_in_progress", "MARK_IN_PROGRESS", "EXIT", {
            "result": "updated" if self.status == self.Status.IN_PROGRESS else "no_change",
            "final_status": self.status,
        })
    # [END_MARK_IN_PROGRESS]
    
    # [START_MARK_COMPLETED]
    """
    ANCHOR: MARK_COMPLETED
    PURPOSE: Отметить модуль как завершённый с возможным указанием балла.

    @PreConditions:
    - экземпляр UserProgress существует

    @PostConditions:
    - статус меняется на COMPLETED
    - completed_at устанавливается в текущее время
    - при наличии score сохраняется результат

    @Invariants:
    - ID записи не меняется
    - user и module не меняются

    @SideEffects:
    - запись в БД (save)
    - установка текущего timestamp

    @ForbiddenChanges:
    - completed_at всегда устанавливается (не сохранять старое значение)
    """
    def mark_completed(self, score=None):
        log_line("progress", "DEBUG", "mark_completed", "MARK_COMPLETED", "ENTRY", {
            "progress_id": self.id,
            "score": str(score) if score else None,
        })
        
        from django.utils import timezone
        
        old_status = self.status
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        
        log_line("progress", "DEBUG", "mark_completed", "MARK_COMPLETED", "STATE_CHANGE", {
            "entity": "progress",
            "id": self.id,
            "status_from": old_status,
            "status_to": "completed",
            "completed_at": self.completed_at.isoformat(),
        })
        
        if score is not None:
            log_line("progress", "DEBUG", "mark_completed", "MARK_COMPLETED", "BRANCH", {
                "branch": "score_provided",
                "score": str(score),
            })
            self.score = score
        
        self.save()
        
        log_line("progress", "INFO", "mark_completed", "MARK_COMPLETED", "EXIT", {
            "result": "completed",
            "progress_id": self.id,
            "score": str(self.score) if self.score else None,
        })
    # [END_MARK_COMPLETED]


# [END_USER_PROGRESS_MODEL]


# === END_CHUNK: PROGRESS_MODELS_V1 ===
