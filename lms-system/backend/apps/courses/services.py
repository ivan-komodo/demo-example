"""Courses services."""

from django.contrib.auth import get_user_model

from .models import Course, CourseEnrollment, Module

User = get_user_model()


# === CHUNK: COURSE_SERVICES_V1 [COURSES] ===
# Описание: Бизнес-логика для управления курсами и записями.
# Dependencies: COURSE_MODELS_V1


# [START_COURSE_SERVICE_CLASS]
# ANCHOR: COURSE_SERVICE_CLASS
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет методы для работы с курсами и записями
# PURPOSE: Сервисный класс для бизнес-логики курсов.
class CourseService:
    """Service for course management."""
    
    # [START_GET_PUBLISHED_COURSES]
    # ANCHOR: GET_PUBLISHED_COURSES
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает QuerySet с опубликованными курсами
    # PURPOSE: Получение всех опубликованных курсов.
    @staticmethod
    def get_published_courses():
        """Get all published courses."""
        return Course.objects.filter(status=Course.Status.PUBLISHED)
    # [END_GET_PUBLISHED_COURSES]
    
    # [START_GET_USER_ENROLLMENTS]
    # ANCHOR: GET_USER_ENROLLMENTS
    # @PreConditions:
    # - user — валидный экземпляр User
    # @PostConditions:
    # - возвращает QuerySet с активными записями пользователя
    # PURPOSE: Получение всех активных записей пользователя на курсы.
    @staticmethod
    def get_user_enrollments(user: User):
        """Get all active enrollments for a user."""
        return CourseEnrollment.objects.filter(
            user=user,
            status=CourseEnrollment.Status.ACTIVE
        ).select_related('course')
    # [END_GET_USER_ENROLLMENTS]
    
    # [START_ENROLL_USER_SERVICE]
    # ANCHOR: ENROLL_USER_SERVICE
    # @PreConditions:
    # - user — валидный экземпляр User
    # - course — валидный экземпляр Course
    # @PostConditions:
    # - возвращает существующую или новую запись CourseEnrollment
    # PURPOSE: Запись пользователя на курс.
    @staticmethod
    def enroll_user(user: User, course: Course) -> CourseEnrollment:
        """Enroll a user in a course."""
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=user,
            course=course,
            defaults={'status': CourseEnrollment.Status.ACTIVE}
        )
        return enrollment
    # [END_ENROLL_USER_SERVICE]
    
    # [START_COMPLETE_ENROLLMENT]
    # ANCHOR: COMPLETE_ENROLLMENT
    # @PreConditions:
    # - enrollment — валидный экземпляр CourseEnrollment
    # @PostConditions:
    # - статус записи изменён на COMPLETED
    # - completed_at установлен в текущее время
    # PURPOSE: Завершение записи на курс.
    @staticmethod
    def complete_enrollment(enrollment: CourseEnrollment):
        """Mark enrollment as completed."""
        from django.utils import timezone
        
        enrollment.status = CourseEnrollment.Status.COMPLETED
        enrollment.completed_at = timezone.now()
        enrollment.save(update_fields=['status', 'completed_at'])
    # [END_COMPLETE_ENROLLMENT]


# [END_COURSE_SERVICE_CLASS]


# === END_CHUNK: COURSE_SERVICES_V1 ===