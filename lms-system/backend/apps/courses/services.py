"""Courses services."""

from django.contrib.auth import get_user_model

from core.utils import log_line

from .models import Course, CourseEnrollment, Module

User = get_user_model()


# === CHUNK: COURSE_SERVICES_V1 [COURSES] ===
# Описание: Бизнес-логика для управления курсами и записями.
# Dependencies: COURSE_MODELS_V1


# [START_COURSE_SERVICE_CLASS]
"""
ANCHOR: COURSE_SERVICE_CLASS
PURPOSE: Сервисный класс для бизнес-логики курсов.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет методы для работы с курсами и записями

@Invariants:
- все методы статические (stateless service)

@SideEffects:
- операции с БД через ORM

@ForbiddenChanges:
- паттерн статических методов (stateless service)
"""
class CourseService:
    """Service for course management."""
    
    # [START_GET_PUBLISHED_COURSES]
    """
    ANCHOR: GET_PUBLISHED_COURSES
    PURPOSE: Получение всех опубликованных курсов.

    @PreConditions:
    - нет нетривиальных предусловий

    @PostConditions:
    - возвращает QuerySet с опубликованными курсами
    - QuerySet не выполнен (lazy evaluation)

    @Invariants:
    - фильтрация только по status=PUBLISHED

    @SideEffects:
    - нет побочных эффектов (QuerySet lazy)

    @ForbiddenChanges:
    - фильтр по статусу PUBLISHED
    """
    @staticmethod
    def get_published_courses():
        """Get all published courses."""
        log_line("courses", "DEBUG", "get_published_courses", "GET_PUBLISHED_COURSES", "ENTRY", {})
        queryset = Course.objects.filter(status=Course.Status.PUBLISHED)
        log_line("courses", "DEBUG", "get_published_courses", "GET_PUBLISHED_COURSES", "EXIT", {
            "filter": "published",
        })
        return queryset
    # [END_GET_PUBLISHED_COURSES]
    
    # [START_GET_USER_ENROLLMENTS]
    """
    ANCHOR: GET_USER_ENROLLMENTS
    PURPOSE: Получение всех активных записей пользователя на курсы.

    @PreConditions:
    - user — валидный экземпляр User

    @PostConditions:
    - возвращает QuerySet с активными записями пользователя
    - QuerySet включает связанные course (select_related)

    @Invariants:
    - фильтрация только по status=ACTIVE

    @SideEffects:
    - нет побочных эффектов (QuerySet lazy)

    @ForbiddenChanges:
    - фильтр по статусу ACTIVE
    - select_related('course')
    """
    @staticmethod
    def get_user_enrollments(user: User):
        """Get all active enrollments for a user."""
        log_line("courses", "DEBUG", "get_user_enrollments", "GET_USER_ENROLLMENTS", "ENTRY", {
            "user_id": user.id,
            "user_email": user.email,
        })
        queryset = CourseEnrollment.objects.filter(
            user=user,
            status=CourseEnrollment.Status.ACTIVE
        ).select_related('course')
        log_line("courses", "DEBUG", "get_user_enrollments", "GET_USER_ENROLLMENTS", "EXIT", {
            "user_id": user.id,
            "filter": "active",
        })
        return queryset
    # [END_GET_USER_ENROLLMENTS]
    
    # [START_ENROLL_USER_SERVICE]
    """
    ANCHOR: ENROLL_USER_SERVICE
    PURPOSE: Запись пользователя на курс.

    @PreConditions:
    - user — валидный экземпляр User
    - course — валидный экземпляр Course

    @PostConditions:
    - при первой записи создаётся новая CourseEnrollment со status=ACTIVE
    - при повторной записи возвращается существующая CourseEnrollment
    - возвращает CourseEnrollment

    @Invariants:
    - одна запись на пару user-course (unique constraint)
    - статус новых записей всегда ACTIVE

    @SideEffects:
    - создание записи в БД при первом вызове

    @ForbiddenChanges:
    - использование get_or_create (атомарность)
    - defaults={'status': CourseEnrollment.Status.ACTIVE}
    """
    @staticmethod
    def enroll_user(user: User, course: Course) -> CourseEnrollment:
        """Enroll a user in a course."""
        log_line("courses", "DEBUG", "enroll_user", "ENROLL_USER_SERVICE", "ENTRY", {
            "user_id": user.id,
            "user_email": user.email,
            "course_id": course.id,
            "course_title": course.title[:50] if course.title else None,
        })
        
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=user,
            course=course,
            defaults={'status': CourseEnrollment.Status.ACTIVE}
        )
        
        log_line("courses", "INFO", "enroll_user", "ENROLL_USER_SERVICE", "STATE_CHANGE", {
            "action": "enrollment_created" if created else "enrollment_exists",
            "enrollment_id": enrollment.id,
            "user_id": user.id,
            "course_id": course.id,
            "created": created,
        })
        
        log_line("courses", "DEBUG", "enroll_user", "ENROLL_USER_SERVICE", "EXIT", {
            "enrollment_id": enrollment.id,
            "created": created,
        })
        return enrollment
    # [END_ENROLL_USER_SERVICE]
    
    # [START_COMPLETE_ENROLLMENT]
    """
    ANCHOR: COMPLETE_ENROLLMENT
    PURPOSE: Завершение записи на курс.

    @PreConditions:
    - enrollment — валидный экземпляр CourseEnrollment

    @PostConditions:
    - статус записи изменён на COMPLETED
    - completed_at установлен в текущее время
    - изменения сохранены в БД

    @Invariants:
    - completed_at всегда устанавливается при смене статуса
    - обновляются только поля status и completed_at

    @SideEffects:
    - запись в БД
    - изменение состояния enrollment объекта

    @ForbiddenChanges:
    - статус COMPLETED
    - использование timezone.now() для completed_at
    - update_fields=['status', 'completed_at']
    """
    @staticmethod
    def complete_enrollment(enrollment: CourseEnrollment):
        """Mark enrollment as completed."""
        log_line("courses", "DEBUG", "complete_enrollment", "COMPLETE_ENROLLMENT", "ENTRY", {
            "enrollment_id": enrollment.id,
            "user_id": enrollment.user_id,
            "course_id": enrollment.course_id,
            "current_status": enrollment.status,
        })
        
        from django.utils import timezone
        
        previous_status = enrollment.status
        enrollment.status = CourseEnrollment.Status.COMPLETED
        enrollment.completed_at = timezone.now()
        enrollment.save(update_fields=['status', 'completed_at'])
        
        log_line("courses", "INFO", "complete_enrollment", "COMPLETE_ENROLLMENT", "STATE_CHANGE", {
            "action": "enrollment_completed",
            "enrollment_id": enrollment.id,
            "previous_status": previous_status,
            "new_status": enrollment.status,
            "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None,
        })
        
        log_line("courses", "DEBUG", "complete_enrollment", "COMPLETE_ENROLLMENT", "EXIT", {
            "enrollment_id": enrollment.id,
            "status": enrollment.status,
        })
    # [END_COMPLETE_ENROLLMENT]


# [END_COURSE_SERVICE_CLASS]


# === END_CHUNK: COURSE_SERVICES_V1 ===
