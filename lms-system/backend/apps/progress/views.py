"""Progress views."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.courses.models import Course

from core.utils import log_line

from .models import UserProgress
from .serializers import CourseProgressSerializer, UserProgressSerializer


# === CHUNK: PROGRESS_VIEWS_V1 [PROGRESS] ===
# Описание: ViewSet для управления прогрессом пользователей.
# Dependencies: PROGRESS_MODELS_V1, PROGRESS_SERIALIZERS_V1


# [START_PROGRESS_VIEWSET]
"""
ANCHOR: PROGRESS_VIEWSET
PURPOSE: ViewSet для управления прогрессом пользователя по модулям.

@PreConditions:
- нет нетривиальных предусловий для объявления класса

@PostConditions:
- предоставляет CRUD операции для прогресса
- предоставляет action для сводки по курсам
- все операции ограничены текущим пользователем

@Invariants:
- permission_classes всегда [IsAuthenticated]
- queryset всегда фильтруется по request.user

@SideEffects:
- нет побочных эффектов на уровне класса

@ForbiddenChanges:
- permission_classes = [IsAuthenticated] (безопасность)
"""
class ProgressViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProgress model."""
    
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]
    
    # [START_GET_QUERYSET_PROGRESS]
    """
    ANCHOR: GET_QUERYSET_PROGRESS
    PURPOSE: Фильтрация прогресса по текущему пользователю и опционально по курсу.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - возвращает только прогресс текущего пользователя
    - при наличии course_id фильтрует по курсу

    @Invariants:
    - результат всегда содержит только записи request.user

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - фильтрация по user=self.request.user (безопасность данных)
    """
    def get_queryset(self):
        log_line("progress", "DEBUG", "get_queryset", "GET_QUERYSET_PROGRESS", "ENTRY", {
            "user_id": self.request.user.id,
        })
        
        queryset = UserProgress.objects.select_related('module', 'module__course').filter(
            user=self.request.user
        )
        course_id = self.request.query_params.get('course_id')
        
        if course_id:
            log_line("progress", "DEBUG", "get_queryset", "GET_QUERYSET_PROGRESS", "BRANCH", {
                "branch": "course_filter",
                "course_id": course_id,
            })
            queryset = queryset.filter(module__course_id=course_id)
        
        result_count = queryset.count()
        log_line("progress", "DEBUG", "get_queryset", "GET_QUERYSET_PROGRESS", "EXIT", {
            "count": result_count,
            "course_filtered": bool(course_id),
        })
        
        return queryset
    # [END_GET_QUERYSET_PROGRESS]
    
    # [START_PERFORM_CREATE_PROGRESS]
    """
    ANCHOR: PERFORM_CREATE_PROGRESS
    PURPOSE: Автоматическое связывание прогресса с текущим пользователем при создании.

    @PreConditions:
    - serializer валиден
    - request.user аутентифицирован

    @PostConditions:
    - создаёт запись прогресса с текущим пользователем

    @Invariants:
    - user всегда берётся из request.user

    @SideEffects:
    - создание записи в БД

    @ForbiddenChanges:
    - user=self.request.user (безопасность - нельзя создать прогресс для другого пользователя)
    """
    def perform_create(self, serializer):
        log_line("progress", "DEBUG", "perform_create", "PERFORM_CREATE_PROGRESS", "ENTRY", {
            "user_id": self.request.user.id,
        })
        
        progress = serializer.save(user=self.request.user)
        
        log_line("progress", "INFO", "perform_create", "PERFORM_CREATE_PROGRESS", "STATE_CHANGE", {
            "entity": "progress",
            "id": progress.id,
            "action": "created",
        })
        
        log_line("progress", "DEBUG", "perform_create", "PERFORM_CREATE_PROGRESS", "EXIT", {
            "result": "success",
            "progress_id": progress.id,
        })
    # [END_PERFORM_CREATE_PROGRESS]
    
    # [START_COURSE_SUMMARY]
    """
    ANCHOR: COURSE_SUMMARY
    PURPOSE: Получение сводки прогресса по всем записанным курсам пользователя.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - возвращает список сводок по курсам
    - каждая сводка содержит: course_id, course_title, total_modules, completed_modules, in_progress_modules, not_started_modules, progress_percentage
    - курсы без модулей пропускаются

    @Invariants:
    - возвращаются только ACTIVE enrollments пользователя

    @SideEffects:
    - нет побочных эффектов (только чтение)

    @ForbiddenChanges:
    - фильтрация по user=request.user и status=ACTIVE (безопасность данных)
    """
    @action(detail=False, methods=['get'])
    def course_summary(self, request):
        log_line("progress", "DEBUG", "course_summary", "COURSE_SUMMARY", "ENTRY", {
            "user_id": request.user.id,
        })
        
        from apps.courses.models import CourseEnrollment
        
        enrollments = CourseEnrollment.objects.filter(
            user=request.user,
            status=CourseEnrollment.Status.ACTIVE
        ).select_related('course')
        
        log_line("progress", "DEBUG", "course_summary", "COURSE_SUMMARY", "CHECK", {
            "enrollments_count": enrollments.count(),
        })
        
        summaries = []
        for enrollment in enrollments:
            course = enrollment.course
            total_modules = course.modules.count()
            
            if total_modules == 0:
                log_line("progress", "DEBUG", "course_summary", "COURSE_SUMMARY", "BRANCH", {
                    "branch": "skip_empty_course",
                    "course_id": course.id,
                })
                continue
            
            progress = UserProgress.objects.filter(
                user=request.user,
                module__course=course
            )
            
            completed = progress.filter(status=UserProgress.Status.COMPLETED).count()
            in_progress = progress.filter(status=UserProgress.Status.IN_PROGRESS).count()
            not_started = total_modules - completed - in_progress
            
            progress_percentage = round((completed / total_modules) * 100, 2) if total_modules > 0 else 0
            
            summary = {
                'course_id': course.id,
                'course_title': course.title,
                'total_modules': total_modules,
                'completed_modules': completed,
                'in_progress_modules': in_progress,
                'not_started_modules': not_started,
                'progress_percentage': progress_percentage,
            }
            
            log_line("progress", "DEBUG", "course_summary", "COURSE_SUMMARY", "DECISION", {
                "decision": "add_summary",
                "course_id": course.id,
                "progress_percentage": progress_percentage,
            })
            
            summaries.append(summary)
        
        log_line("progress", "INFO", "course_summary", "COURSE_SUMMARY", "EXIT", {
            "result": "success",
            "summaries_count": len(summaries),
        })
        
        return Response(summaries)
    # [END_COURSE_SUMMARY]


# [END_PROGRESS_VIEWSET]


# === END_CHUNK: PROGRESS_VIEWS_V1 ===
