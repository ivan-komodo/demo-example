"""Progress views."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.courses.models import Course

from .models import UserProgress
from .serializers import CourseProgressSerializer, UserProgressSerializer


# === CHUNK: PROGRESS_VIEWS_V1 [PROGRESS] ===
# Описание: ViewSet для управления прогрессом пользователей.
# Dependencies: PROGRESS_MODELS_V1, PROGRESS_SERIALIZERS_V1


# [START_PROGRESS_VIEWSET]
# ANCHOR: PROGRESS_VIEWSET
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет CRUD операции для прогресса
# - предоставляет action для сводки по курсам
# PURPOSE: ViewSet для управления прогрессом пользователя по модулям.
class ProgressViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProgress model."""
    
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]
    
    # [START_GET_QUERYSET_PROGRESS]
    # ANCHOR: GET_QUERYSET_PROGRESS
    # @PreConditions:
    # - request.user аутентифицирован
    # @PostConditions:
    # - возвращает только прогресс текущего пользователя
    # - при наличии course_id фильтрует по курсу
    # PURPOSE: Фильтрация прогресса по пользователю и курсу.
    def get_queryset(self):
        queryset = UserProgress.objects.select_related('module', 'module__course').filter(
            user=self.request.user
        )
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(module__course_id=course_id)
        return queryset
    # [END_GET_QUERYSET_PROGRESS]
    
    # [START_PERFORM_CREATE_PROGRESS]
    # ANCHOR: PERFORM_CREATE_PROGRESS
    # @PreConditions:
    # - serializer валиден
    # - request.user аутентифицирован
    # @PostConditions:
    # - создаёт запись прогресса с текущим пользователем
    # PURPOSE: Автоматическое связывание прогресса с текущим пользователем.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # [END_PERFORM_CREATE_PROGRESS]
    
    # [START_COURSE_SUMMARY]
    # ANCHOR: COURSE_SUMMARY
    # @PreConditions:
    # - request.user аутентифицирован
    # @PostConditions:
    # - возвращает сводку прогресса по всем активным курсам пользователя
    # PURPOSE: Получение сводки прогресса по всем записанным курсам.
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
    # [END_COURSE_SUMMARY]


# [END_PROGRESS_VIEWSET]


# === END_CHUNK: PROGRESS_VIEWS_V1 ===