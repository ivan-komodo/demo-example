"""Courses services."""

from django.contrib.auth import get_user_model

from .models import Course, CourseEnrollment, Module

User = get_user_model()


class CourseService:
    """Service for course management."""
    
    @staticmethod
    def get_published_courses():
        """Get all published courses."""
        return Course.objects.filter(status=Course.Status.PUBLISHED)
    
    @staticmethod
    def get_user_enrollments(user: User):
        """Get all active enrollments for a user."""
        return CourseEnrollment.objects.filter(
            user=user,
            status=CourseEnrollment.Status.ACTIVE
        ).select_related('course')
    
    @staticmethod
    def enroll_user(user: User, course: Course) -> CourseEnrollment:
        """Enroll a user in a course."""
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=user,
            course=course,
            defaults={'status': CourseEnrollment.Status.ACTIVE}
        )
        return enrollment
    
    @staticmethod
    def complete_enrollment(enrollment: CourseEnrollment):
        """Mark enrollment as completed."""
        from django.utils import timezone
        
        enrollment.status = CourseEnrollment.Status.COMPLETED
        enrollment.completed_at = timezone.now()
        enrollment.save(update_fields=['status', 'completed_at'])