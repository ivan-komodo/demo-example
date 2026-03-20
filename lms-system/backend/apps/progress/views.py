"""Progress views."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.courses.models import Course

from .models import UserProgress
from .serializers import CourseProgressSerializer, UserProgressSerializer


class ProgressViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProgress model."""
    
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = UserProgress.objects.select_related('module', 'module__course').filter(
            user=self.request.user
        )
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(module__course_id=course_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def course_summary(self, request):
        """Get progress summary for all enrolled courses."""
        from apps.courses.models import CourseEnrollment
        
        enrollments = CourseEnrollment.objects.filter(
            user=request.user,
            status=CourseEnrollment.Status.ACTIVE
        ).select_related('course')
        
        summaries = []
        for enrollment in enrollments:
            course = enrollment.course
            total_modules = course.modules.count()
            
            if total_modules == 0:
                continue
            
            progress = UserProgress.objects.filter(
                user=request.user,
                module__course=course
            )
            
            completed = progress.filter(status=UserProgress.Status.COMPLETED).count()
            in_progress = progress.filter(status=UserProgress.Status.IN_PROGRESS).count()
            not_started = total_modules - completed - in_progress
            
            summaries.append({
                'course_id': course.id,
                'course_title': course.title,
                'total_modules': total_modules,
                'completed_modules': completed,
                'in_progress_modules': in_progress,
                'not_started_modules': not_started,
                'progress_percentage': round((completed / total_modules) * 100, 2) if total_modules > 0 else 0,
            })
        
        return Response(summaries)