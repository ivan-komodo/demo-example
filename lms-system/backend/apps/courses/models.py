"""
Course models for LMS System.

This module contains models for courses, modules, and course enrollments.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils import log_line


# === CHUNK: COURSE_MODELS_V1 [COURSES] ===
# Описание: Модели для управления курсами, модулями и записями на курсы.
# Dependencies: USER_MODEL_V1, PROGRESS_MODELS_V1


# [START_COURSE_MODEL]
"""
ANCHOR: COURSE_MODEL
PURPOSE: Модель для хранения информации о курсах.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет модель курса с полями title, description, status
- при сохранении устанавливается created_at и updated_at

@Invariants:
- статус всегда один из draft, published, archived
- title не может быть пустым

@SideEffects:
- создание таблицы courses в БД при миграции

@ForbiddenChanges:
- поле id (автоинкрементный первичный ключ)
- названия статусов (draft, published, archived)
"""
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
    """
    ANCHOR: COURSE_STR
    PURPOSE: Строковое представление курса для админки и отладки.

    @PreConditions:
    - экземпляр Course существует

    @PostConditions:
    - возвращает строковое представление курса (title)

    @Invariants:
    - всегда возвращает строку

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - возвращаемое значение всегда self.title
    """
    def __str__(self):
        return self.title
    # [END_COURSE_STR]
    
    # [START_MODULES_COUNT]
    """
    ANCHOR: MODULES_COUNT
    PURPOSE: Получение количества модулей в курсе.

    @PreConditions:
    - экземпляр Course существует

    @PostConditions:
    - возвращает количество модулей в курсе (int)

    @Invariants:
    - всегда возвращает неотрицательное число

    @SideEffects:
    - выполняет SQL запрос к связанной таблице modules

    @ForbiddenChanges:
    - результат всегда int (не QuerySet)
    """
    @property
    def modules_count(self):
        """Return the number of modules in this course."""
        log_line("courses", "DEBUG", "modules_count", "MODULES_COUNT", "ENTRY", {
            "course_id": self.id,
            "course_title": self.title[:50] if self.title else None,
        })
        count = self.modules.count()
        log_line("courses", "DEBUG", "modules_count", "MODULES_COUNT", "EXIT", {
            "course_id": self.id,
            "count": count,
        })
        return count
    # [END_MODULES_COUNT]
    
    # [START_ENROLLED_COUNT]
    """
    ANCHOR: ENROLLED_COUNT
    PURPOSE: Получение количества активных записей на курс.

    @PreConditions:
    - экземпляр Course существует

    @PostConditions:
    - возвращает количество активных записей на курс (int)

    @Invariants:
    - всегда возвращает неотрицательное число
    - считает только записи со status='active'

    @SideEffects:
    - выполняет SQL запрос к связанной таблице enrollments

    @ForbiddenChanges:
    - фильтр по status='active'
    """
    @property
    def enrolled_count(self):
        """Return the number of enrolled users."""
        log_line("courses", "DEBUG", "enrolled_count", "ENROLLED_COUNT", "ENTRY", {
            "course_id": self.id,
            "course_title": self.title[:50] if self.title else None,
        })
        count = self.enrollments.filter(status='active').count()
        log_line("courses", "DEBUG", "enrolled_count", "ENROLLED_COUNT", "EXIT", {
            "course_id": self.id,
            "count": count,
        })
        return count
    # [END_ENROLLED_COUNT]


# [END_COURSE_MODEL]


# [START_MODULE_MODEL]
"""
ANCHOR: MODULE_MODEL
PURPOSE: Модель для хранения модулей курса с контентом.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет модель модуля с полями course, title, content_type, order_num
- при сохранении устанавливается created_at и updated_at

@Invariants:
- связь с курсом обязательна (course not null)
- content_type всегда один из text, pdf, video
- order_num автоматически инкрементируется при отсутствии

@SideEffects:
- создание таблицы modules в БД при миграции

@ForbiddenChanges:
- поле id (автоинкрементный первичный ключ)
- foreign key связь с Course
"""
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
    """
    ANCHOR: MODULE_STR
    PURPOSE: Строковое представление модуля для админки и отладки.

    @PreConditions:
    - экземпляр Module существует

    @PostConditions:
    - возвращает строку вида "Название курса - Название модуля"

    @Invariants:
    - всегда возвращает строку

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - формат вывода "course.title - title"
    """
    def __str__(self):
        return f'{self.course.title} - {self.title}'
    # [END_MODULE_STR]
    
    # [START_MODULE_SAVE]
    """
    ANCHOR: MODULE_SAVE
    PURPOSE: Автоматическая установка порядкового номера модуля при создании.

    @PreConditions:
    - экземпляр Module инициализирован

    @PostConditions:
    - при отсутствии order_num устанавливается следующий по порядку номер
    - экземпляр сохранён в БД

    @Invariants:
    - order_num всегда положительное число
    - существующий order_num не изменяется

    @SideEffects:
    - запись в БД
    - SQL запрос для определения максимального order_num

    @ForbiddenChanges:
    - логика автоинкремента order_num (max_order + 1)
    """
    def save(self, *args, **kwargs):
        """Auto-set order_num if not provided."""
        log_line("courses", "DEBUG", "save", "MODULE_SAVE", "ENTRY", {
            "module_id": self.id,
            "course_id": self.course_id,
            "title": self.title[:50] if self.title else None,
            "order_num": self.order_num,
            "is_new": self.pk is None,
        })
        
        if not self.order_num:
            max_order = Module.objects.filter(course=self.course).aggregate(
                max_order=models.Max('order_num')
            )['max_order']
            new_order = (max_order or 0) + 1
            self.order_num = new_order
            log_line("courses", "DEBUG", "save", "MODULE_SAVE", "STATE_CHANGE", {
                "action": "auto_order_num",
                "order_num": new_order,
                "previous_max": max_order,
            })
        
        super().save(*args, **kwargs)
        log_line("courses", "DEBUG", "save", "MODULE_SAVE", "EXIT", {
            "module_id": self.id,
            "order_num": self.order_num,
        })
    # [END_MODULE_SAVE]


# [END_MODULE_MODEL]


# [START_COURSE_ENROLLMENT_MODEL]
"""
ANCHOR: COURSE_ENROLLMENT_MODEL
PURPOSE: Модель для отслеживания записей пользователей на курсы.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет модель записи на курс с полями user, course, status
- при сохранении устанавливается enrolled_at

@Invariants:
- пара user-course уникальна
- статус всегда один из active, completed, dropped

@SideEffects:
- создание таблицы course_enrollments в БД при миграции

@ForbiddenChanges:
- поле id (автоинкрементный первичный ключ)
- unique_together constraint ['user', 'course']
"""
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
    """
    ANCHOR: ENROLLMENT_STR
    PURPOSE: Строковое представление записи для админки и отладки.

    @PreConditions:
    - экземпляр CourseEnrollment существует

    @PostConditions:
    - возвращает строку вида "email пользователя - название курса"

    @Invariants:
    - всегда возвращает строку

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - формат вывода "user.email - course.title"
    """
    def __str__(self):
        return f'{self.user.email} - {self.course.title}'
    # [END_ENROLLMENT_STR]
    
    # [START_PROGRESS_PERCENTAGE]
    """
    ANCHOR: PROGRESS_PERCENTAGE
    PURPOSE: Расчёт процента прогресса по курсу для данной записи.

    @PreConditions:
    - экземпляр CourseEnrollment существует
    - модуль UserProgress доступен для импорта

    @PostConditions:
    - возвращает процент завершения курса (0-100)
    - при отсутствии модулей возвращает 0

    @Invariants:
    - результат всегда число от 0 до 100
    - округление до 2 знаков после запятой

    @SideEffects:
    - SQL запрос к таблице user_progress
    - импорт apps.progress.models (избежание циклического импорта)

    @ForbiddenChanges:
    - расчёт только по status='completed' модулям
    - округление round(x, 2)
    """
    @property
    def progress_percentage(self):
        """Calculate progress percentage for this enrollment."""
        log_line("courses", "DEBUG", "progress_percentage", "PROGRESS_PERCENTAGE", "ENTRY", {
            "enrollment_id": self.id,
            "user_id": self.user_id,
            "course_id": self.course_id,
        })
        
        total_modules = self.course.modules.count()
        log_line("courses", "DEBUG", "progress_percentage", "PROGRESS_PERCENTAGE", "CHECK", {
            "total_modules": total_modules,
        })
        
        if total_modules == 0:
            log_line("courses", "DEBUG", "progress_percentage", "PROGRESS_PERCENTAGE", "BRANCH", {
                "branch": "no_modules",
            })
            log_line("courses", "DEBUG", "progress_percentage", "PROGRESS_PERCENTAGE", "EXIT", {
                "percentage": 0,
                "reason": "no_modules",
            })
            return 0
        
        from apps.progress.models import UserProgress
        
        completed_modules = UserProgress.objects.filter(
            user=self.user,
            module__course=self.course,
            status='completed',
        ).count()
        
        percentage = round((completed_modules / total_modules) * 100, 2)
        
        log_line("courses", "DEBUG", "progress_percentage", "PROGRESS_PERCENTAGE", "EXIT", {
            "percentage": percentage,
            "completed_modules": completed_modules,
            "total_modules": total_modules,
        })
        return percentage
    # [END_PROGRESS_PERCENTAGE]


# [END_COURSE_ENROLLMENT_MODEL]


# === END_CHUNK: COURSE_MODELS_V1 ===
