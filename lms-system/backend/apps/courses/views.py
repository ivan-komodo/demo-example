"""
Course views for LMS System.
"""

from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsAdminUser
from core.utils import log_line

from .models import Course, CourseEnrollment, Module
from .serializers import (
    CourseCreateSerializer,
    CourseEnrollmentSerializer,
    CourseListSerializer,
    CourseSerializer,
    EnrollUserSerializer,
    ModuleCreateSerializer,
    ModuleSerializer,
)

User = get_user_model()


# === CHUNK: COURSE_VIEWS_V1 [COURSES] ===
# Описание: ViewSet-ы для управления курсами, модулями и записями.
# Dependencies: COURSE_MODELS_V1, COURSE_SERIALIZERS_V1


# [START_COURSE_VIEWSET]
"""
ANCHOR: COURSE_VIEWSET
PURPOSE: ViewSet для управления курсами с разграничением прав доступа.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет CRUD операции для курсов
- администраторы могут создавать, обновлять, удалять курсы
- обычные пользователи видят только опубликованные курсы

@Invariants:
- аутентификация обязательна для всех действий
- фильтрация по статусу для не-администраторов

@SideEffects:
- операции с БД через ORM
- ответы HTTP

@ForbiddenChanges:
- permission_classes = [IsAuthenticated]
- фильтрация queryset для не-администраторов
"""
class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Course model.
    
    Provides CRUD operations for courses.
    Only admins can create, update, or delete courses.
    """
    
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    
    # [START_GET_SERIALIZER_CLASS_COURSE]
    """
    ANCHOR: GET_SERIALIZER_CLASS_COURSE
    PURPOSE: Выбор сериализатора в зависимости от действия.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - возвращает CourseCreateSerializer для create
    - возвращает CourseListSerializer для list
    - возвращает CourseSerializer для остальных действий

    @Invariants:
    - action всегда определён

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - соответствие action и serializer
    """
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        log_line("courses", "DEBUG", "get_serializer_class", "GET_SERIALIZER_CLASS_COURSE", "ENTRY", {
            "action": self.action,
        })
        
        if self.action == 'create':
            serializer_class = CourseCreateSerializer
        elif self.action == 'list':
            serializer_class = CourseListSerializer
        else:
            serializer_class = CourseSerializer
        
        log_line("courses", "DEBUG", "get_serializer_class", "GET_SERIALIZER_CLASS_COURSE", "EXIT", {
            "serializer": serializer_class.__name__,
        })
        return serializer_class
    # [END_GET_SERIALIZER_CLASS_COURSE]
    
    # [START_GET_QUERYSET_COURSE]
    """
    ANCHOR: GET_QUERYSET_COURSE
    PURPOSE: Фильтрация queryset в зависимости от роли пользователя.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - для администраторов возвращает все курсы
    - для остальных — только опубликованные

    @Invariants:
    - prefetch_related('modules') всегда применяется

    @SideEffects:
    - нет побочных эффектов (QuerySet lazy)

    @ForbiddenChanges:
    - фильтр по status='published' для не-администраторов
    """
    def get_queryset(self):
        """Filter queryset based on user role."""
        log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_COURSE", "ENTRY", {
            "user_id": self.request.user.id,
            "is_admin": self.request.user.is_admin,
        })
        
        queryset = Course.objects.prefetch_related('modules')
        
        if self.request.user.is_admin:
            log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_COURSE", "BRANCH", {
                "branch": "admin_all_courses",
            })
            log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_COURSE", "EXIT", {
                "filter": "none",
            })
            return queryset
        
        log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_COURSE", "BRANCH", {
            "branch": "published_only",
        })
        result = queryset.filter(status='published')
        log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_COURSE", "EXIT", {
            "filter": "published",
        })
        return result
    # [END_GET_QUERYSET_COURSE]
    
    # [START_PERFORM_CREATE_COURSE]
    """
    ANCHOR: PERFORM_CREATE_COURSE
    PURPOSE: Создание нового курса.

    @PreConditions:
    - serializer валиден
    - request.user — администратор

    @PostConditions:
    - курс создан и сохранён в БД

    @Invariants:
    - serializer.save() вызывается корректно

    @SideEffects:
    - создание записи в БД

    @ForbiddenChanges:
    - вызов serializer.save()
    """
    def perform_create(self, serializer):
        """Create a new course."""
        log_line("courses", "DEBUG", "perform_create", "PERFORM_CREATE_COURSE", "ENTRY", {
            "user_id": self.request.user.id,
        })
        instance = serializer.save()
        log_line("courses", "INFO", "perform_create", "PERFORM_CREATE_COURSE", "STATE_CHANGE", {
            "action": "course_created",
            "course_id": instance.id,
            "course_title": instance.title[:50] if instance.title else None,
            "status": instance.status,
        })
        log_line("courses", "DEBUG", "perform_create", "PERFORM_CREATE_COURSE", "EXIT", {
            "course_id": instance.id,
        })
    # [END_PERFORM_CREATE_COURSE]
    
    # [START_PERFORM_UPDATE_COURSE]
    """
    ANCHOR: PERFORM_UPDATE_COURSE
    PURPOSE: Обновление существующего курса.

    @PreConditions:
    - serializer валиден
    - request.user — администратор

    @PostConditions:
    - курс обновлён в БД

    @Invariants:
    - serializer.save() вызывается корректно

    @SideEffects:
    - обновление записи в БД

    @ForbiddenChanges:
    - вызов serializer.save()
    """
    def perform_update(self, serializer):
        """Update a course."""
        log_line("courses", "DEBUG", "perform_update", "PERFORM_UPDATE_COURSE", "ENTRY", {
            "user_id": self.request.user.id,
            "course_id": self.get_object().id,
        })
        instance = serializer.save()
        log_line("courses", "INFO", "perform_update", "PERFORM_UPDATE_COURSE", "STATE_CHANGE", {
            "action": "course_updated",
            "course_id": instance.id,
            "course_title": instance.title[:50] if instance.title else None,
        })
        log_line("courses", "DEBUG", "perform_update", "PERFORM_UPDATE_COURSE", "EXIT", {
            "course_id": instance.id,
        })
    # [END_PERFORM_UPDATE_COURSE]
    
    # [START_PERFORM_DESTROY_COURSE]
    """
    ANCHOR: PERFORM_DESTROY_COURSE
    PURPOSE: Удаление курса.

    @PreConditions:
    - instance существует
    - request.user — администратор

    @PostConditions:
    - курс удалён из БД

    @Invariants:
    - instance.delete() вызывается корректно

    @SideEffects:
    - удаление записи из БД
    - каскадное удаление связанных модулей и записей

    @ForbiddenChanges:
    - вызов instance.delete()
    """
    def perform_destroy(self, instance):
        """Delete a course."""
        log_line("courses", "DEBUG", "perform_destroy", "PERFORM_DESTROY_COURSE", "ENTRY", {
            "user_id": self.request.user.id,
            "course_id": instance.id,
            "course_title": instance.title[:50] if instance.title else None,
        })
        course_id = instance.id
        instance.delete()
        log_line("courses", "INFO", "perform_destroy", "PERFORM_DESTROY_COURSE", "STATE_CHANGE", {
            "action": "course_deleted",
            "course_id": course_id,
        })
        log_line("courses", "DEBUG", "perform_destroy", "PERFORM_DESTROY_COURSE", "EXIT", {
            "course_id": course_id,
        })
    # [END_PERFORM_DESTROY_COURSE]
    
    # [START_PUBLISH_COURSE]
    """
    ANCHOR: PUBLISH_COURSE
    PURPOSE: Публикация курса (смена статуса на published).

    @PreConditions:
    - курс существует
    - request.user — администратор

    @PostConditions:
    - статус курса изменён на PUBLISHED
    - возвращён ответ с сообщением об успехе

    @Invariants:
    - публикация возможна из любого статуса

    @SideEffects:
    - обновление записи в БД
    - HTTP ответ

    @ForbiddenChanges:
    - статус PUBLISHED
    - update_fields=['status']
    """
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def publish(self, request, pk=None):
        """Publish a course."""
        log_line("courses", "DEBUG", "publish", "PUBLISH_COURSE", "ENTRY", {
            "user_id": request.user.id,
            "course_pk": pk,
        })
        
        course = self.get_object()
        previous_status = course.status
        course.status = Course.Status.PUBLISHED
        course.save(update_fields=['status'])
        
        log_line("courses", "INFO", "publish", "PUBLISH_COURSE", "STATE_CHANGE", {
            "action": "course_published",
            "course_id": course.id,
            "previous_status": previous_status,
            "new_status": course.status,
        })
        log_line("courses", "DEBUG", "publish", "PUBLISH_COURSE", "EXIT", {
            "course_id": course.id,
        })
        return Response({'message': 'Курс опубликован.'})
    # [END_PUBLISH_COURSE]
    
    # [START_ARCHIVE_COURSE]
    """
    ANCHOR: ARCHIVE_COURSE
    PURPOSE: Архивирование курса (смена статуса на archived).

    @PreConditions:
    - курс существует
    - request.user — администратор

    @PostConditions:
    - статус курса изменён на ARCHIVED
    - возвращён ответ с сообщением об успехе

    @Invariants:
    - архивация возможна из любого статуса

    @SideEffects:
    - обновление записи в БД
    - HTTP ответ

    @ForbiddenChanges:
    - статус ARCHIVED
    - update_fields=['status']
    """
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def archive(self, request, pk=None):
        """Archive a course."""
        log_line("courses", "DEBUG", "archive", "ARCHIVE_COURSE", "ENTRY", {
            "user_id": request.user.id,
            "course_pk": pk,
        })
        
        course = self.get_object()
        previous_status = course.status
        course.status = Course.Status.ARCHIVED
        course.save(update_fields=['status'])
        
        log_line("courses", "INFO", "archive", "ARCHIVE_COURSE", "STATE_CHANGE", {
            "action": "course_archived",
            "course_id": course.id,
            "previous_status": previous_status,
            "new_status": course.status,
        })
        log_line("courses", "DEBUG", "archive", "ARCHIVE_COURSE", "EXIT", {
            "course_id": course.id,
        })
        return Response({'message': 'Курс архивирован.'})
    # [END_ARCHIVE_COURSE]
    
    # [START_ENROLL_SELF]
    """
    ANCHOR: ENROLL_SELF
    PURPOSE: Запись текущего пользователя на курс.

    @PreConditions:
    - курс существует и опубликован
    - request.user аутентифицирован

    @PostConditions:
    - при успехе создаётся запись CourseEnrollment
    - при повторной записи возвращается ошибка 400
    - при неопубликованном курсе возвращается ошибка 400

    @Invariants:
    - один пользователь может иметь только одну активную запись на курс

    @SideEffects:
    - создание записи в БД
    - HTTP ответ

    @ForbiddenChanges:
    - фильтр по status=PUBLISHED
    - использование get_or_create
    """
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """Enroll current user in the course."""
        log_line("courses", "DEBUG", "enroll", "ENROLL_SELF", "ENTRY", {
            "user_id": request.user.id,
            "course_pk": pk,
        })
        
        course = self.get_object()
        
        log_line("courses", "DEBUG", "enroll", "ENROLL_SELF", "CHECK", {
            "course_id": course.id,
            "course_status": course.status,
        })
        
        if course.status != Course.Status.PUBLISHED:
            log_line("courses", "WARN", "enroll", "ENROLL_SELF", "ERROR", {
                "reason": "course_not_published",
                "course_id": course.id,
                "course_status": course.status,
            })
            log_line("courses", "DEBUG", "enroll", "ENROLL_SELF", "EXIT", {
                "result": "error",
                "error": "course_not_published",
            })
            return Response(
                {'error': 'Невозможно записаться на неопубликованный курс.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'status': CourseEnrollment.Status.ACTIVE}
        )
        
        log_line("courses", "DEBUG", "enroll", "ENROLL_SELF", "DECISION", {
            "created": created,
            "enrollment_id": enrollment.id,
        })
        
        if not created:
            log_line("courses", "WARN", "enroll", "ENROLL_SELF", "ERROR", {
                "reason": "already_enrolled",
                "user_id": request.user.id,
                "course_id": course.id,
            })
            log_line("courses", "DEBUG", "enroll", "ENROLL_SELF", "EXIT", {
                "result": "error",
                "error": "already_enrolled",
            })
            return Response(
                {'error': 'Вы уже записаны на этот курс.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        log_line("courses", "INFO", "enroll", "ENROLL_SELF", "STATE_CHANGE", {
            "action": "user_enrolled",
            "user_id": request.user.id,
            "course_id": course.id,
            "enrollment_id": enrollment.id,
        })
        log_line("courses", "DEBUG", "enroll", "ENROLL_SELF", "EXIT", {
            "result": "success",
            "enrollment_id": enrollment.id,
        })
        return Response(
            CourseEnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )
    # [END_ENROLL_SELF]
    
    # [START_MY_COURSES]
    """
    ANCHOR: MY_COURSES
    PURPOSE: Получение курсов, на которые записан текущий пользователь.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - возвращает список активных записей пользователя на курсы

    @Invariants:
    - фильтрация только по status=ACTIVE

    @SideEffects:
    - SQL запрос к БД
    - HTTP ответ

    @ForbiddenChanges:
    - фильтр по user=request.user
    - фильтр по status=ACTIVE
    - select_related('course')
    """
    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        """Return courses the current user is enrolled in."""
        log_line("courses", "DEBUG", "my_courses", "MY_COURSES", "ENTRY", {
            "user_id": request.user.id,
        })
        
        enrollments = CourseEnrollment.objects.filter(
            user=request.user,
            status=CourseEnrollment.Status.ACTIVE
        ).select_related('course')
        
        serializer = CourseEnrollmentSerializer(enrollments, many=True)
        
        log_line("courses", "DEBUG", "my_courses", "MY_COURSES", "EXIT", {
            "user_id": request.user.id,
            "enrollments_count": len(serializer.data),
        })
        return Response(serializer.data)
    # [END_MY_COURSES]


# [END_COURSE_VIEWSET]


# [START_MODULE_VIEWSET]
"""
ANCHOR: MODULE_VIEWSET
PURPOSE: ViewSet для управления модулями курсов.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет CRUD операции для модулей

@Invariants:
- аутентификация обязательна для всех действий

@SideEffects:
- операции с БД через ORM
- ответы HTTP

@ForbiddenChanges:
- permission_classes = [IsAuthenticated]
"""
class ModuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Module model.
    
    Provides CRUD operations for modules.
    Only admins can create, update, or delete modules.
    """
    
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
    
    # [START_GET_SERIALIZER_CLASS_MODULE]
    """
    ANCHOR: GET_SERIALIZER_CLASS_MODULE
    PURPOSE: Выбор сериализатора в зависимости от действия.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - возвращает ModuleCreateSerializer для create
    - возвращает ModuleSerializer для остальных действий

    @Invariants:
    - action всегда определён

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - соответствие action и serializer
    """
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        log_line("courses", "DEBUG", "get_serializer_class", "GET_SERIALIZER_CLASS_MODULE", "ENTRY", {
            "action": self.action,
        })
        
        if self.action == 'create':
            serializer_class = ModuleCreateSerializer
        else:
            serializer_class = ModuleSerializer
        
        log_line("courses", "DEBUG", "get_serializer_class", "GET_SERIALIZER_CLASS_MODULE", "EXIT", {
            "serializer": serializer_class.__name__,
        })
        return serializer_class
    # [END_GET_SERIALIZER_CLASS_MODULE]
    
    # [START_GET_QUERYSET_MODULE]
    """
    ANCHOR: GET_QUERYSET_MODULE
    PURPOSE: Фильтрация модулей по курсу через query-параметры.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - при наличии course_id фильтрует модули по курсу
    - возвращает QuerySet с select_related('course')

    @Invariants:
    - select_related('course') всегда применяется

    @SideEffects:
    - нет побочных эффектов (QuerySet lazy)

    @ForbiddenChanges:
    - фильтрация по query параметру course_id
    """
    def get_queryset(self):
        """Filter modules by course."""
        log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_MODULE", "ENTRY", {
            "user_id": self.request.user.id,
        })
        
        queryset = Module.objects.select_related('course')
        course_id = self.request.query_params.get('course_id')
        
        log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_MODULE", "CHECK", {
            "course_id": course_id,
        })
        
        if course_id:
            log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_MODULE", "BRANCH", {
                "branch": "filter_by_course",
                "course_id": course_id,
            })
            queryset = queryset.filter(course_id=course_id)
        
        log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_MODULE", "EXIT", {
            "course_id_filter": course_id,
        })
        return queryset
    # [END_GET_QUERYSET_MODULE]
    
    # [START_PERFORM_CREATE_MODULE]
    """
    ANCHOR: PERFORM_CREATE_MODULE
    PURPOSE: Создание нового модуля.

    @PreConditions:
    - serializer валиден
    - request.user — администратор

    @PostConditions:
    - модуль создан и сохранён в БД

    @Invariants:
    - serializer.save() вызывается корректно

    @SideEffects:
    - создание записи в БД

    @ForbiddenChanges:
    - вызов serializer.save()
    """
    def perform_create(self, serializer):
        """Create a new module."""
        log_line("courses", "DEBUG", "perform_create", "PERFORM_CREATE_MODULE", "ENTRY", {
            "user_id": self.request.user.id,
        })
        instance = serializer.save()
        log_line("courses", "INFO", "perform_create", "PERFORM_CREATE_MODULE", "STATE_CHANGE", {
            "action": "module_created",
            "module_id": instance.id,
            "module_title": instance.title[:50] if instance.title else None,
            "course_id": instance.course_id,
        })
        log_line("courses", "DEBUG", "perform_create", "PERFORM_CREATE_MODULE", "EXIT", {
            "module_id": instance.id,
        })
    # [END_PERFORM_CREATE_MODULE]


# [END_MODULE_VIEWSET]


# [START_ENROLLMENT_VIEWSET]
"""
ANCHOR: ENROLLMENT_VIEWSET
PURPOSE: ViewSet для управления записями пользователей на курсы.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет операции для управления записями на курсы

@Invariants:
- аутентификация обязательна для всех действий
- не-администраторы видят только свои записи

@SideEffects:
- операции с БД через ORM
- ответы HTTP

@ForbiddenChanges:
- permission_classes = [IsAuthenticated]
- фильтрация queryset для не-администраторов
"""
class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CourseEnrollment model.
    
    Provides operations for managing course enrollments.
    """
    
    queryset = CourseEnrollment.objects.all()
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'course', 'status']
    
    # [START_GET_QUERYSET_ENROLLMENT]
    """
    ANCHOR: GET_QUERYSET_ENROLLMENT
    PURPOSE: Фильтрация записей в зависимости от роли пользователя.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - для администраторов возвращает все записи
    - для остальных — только свои записи

    @Invariants:
    - select_related('user', 'course') всегда применяется

    @SideEffects:
    - нет побочных эффектов (QuerySet lazy)

    @ForbiddenChanges:
    - фильтр по user=request.user для не-администраторов
    """
    def get_queryset(self):
        """Filter queryset based on user role."""
        log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_ENROLLMENT", "ENTRY", {
            "user_id": self.request.user.id,
            "is_admin": self.request.user.is_admin,
        })
        
        queryset = CourseEnrollment.objects.select_related('user', 'course')
        
        if self.request.user.is_admin:
            log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_ENROLLMENT", "BRANCH", {
                "branch": "admin_all_enrollments",
            })
            log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_ENROLLMENT", "EXIT", {
                "filter": "none",
            })
            return queryset
        
        log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_ENROLLMENT", "BRANCH", {
            "branch": "user_own_enrollments",
        })
        result = queryset.filter(user=self.request.user)
        log_line("courses", "DEBUG", "get_queryset", "GET_QUERYSET_ENROLLMENT", "EXIT", {
            "filter": "own",
        })
        return result
    # [END_GET_QUERYSET_ENROLLMENT]
    
    # [START_ENROLL_USER]
    """
    ANCHOR: ENROLL_USER
    PURPOSE: Запись конкретного пользователя на курс (для администраторов).

    @PreConditions:
    - request.user — администратор
    - request.data содержит user_id и course_id

    @PostConditions:
    - при успехе создаётся запись CourseEnrollment для указанного пользователя
    - при ошибке возвращается соответствующий ответ 400/404

    @Invariants:
    - только администраторы могут вызывать этот метод

    @SideEffects:
    - создание записи в БД
    - HTTP ответ

    @ForbiddenChanges:
    - permission_classes=[IsAdminUser]
    - проверка существования user и course
    - проверка статуса курса PUBLISHED
    """
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def enroll_user(self, request):
        """Enroll a specific user in a course."""
        log_line("courses", "DEBUG", "enroll_user", "ENROLL_USER", "ENTRY", {
            "admin_user_id": request.user.id,
        })
        
        serializer = EnrollUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        course_id = serializer.validated_data['course_id']
        
        log_line("courses", "DEBUG", "enroll_user", "ENROLL_USER", "CHECK", {
            "target_user_id": user_id,
            "course_id": course_id,
        })
        
        try:
            user = User.objects.get(id=user_id)
            course = Course.objects.get(id=course_id)
        except User.DoesNotExist:
            log_line("courses", "WARN", "enroll_user", "ENROLL_USER", "ERROR", {
                "reason": "user_not_found",
                "user_id": user_id,
            })
            log_line("courses", "DEBUG", "enroll_user", "ENROLL_USER", "EXIT", {
                "result": "error",
                "error": "user_not_found",
            })
            return Response(
                {'error': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Course.DoesNotExist:
            log_line("courses", "WARN", "enroll_user", "ENROLL_USER", "ERROR", {
                "reason": "course_not_found",
                "course_id": course_id,
            })
            log_line("courses", "DEBUG", "enroll_user", "ENROLL_USER", "EXIT", {
                "result": "error",
                "error": "course_not_found",
            })
            return Response(
                {'error': 'Курс не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        log_line("courses", "DEBUG", "enroll_user", "ENROLL_USER", "CHECK", {
            "course_status": course.status,
        })
        
        if course.status != Course.Status.PUBLISHED:
            log_line("courses", "WARN", "enroll_user", "ENROLL_USER", "ERROR", {
                "reason": "course_not_published",
                "course_id": course.id,
                "course_status": course.status,
            })
            log_line("courses", "DEBUG", "enroll_user", "ENROLL_USER", "EXIT", {
                "result": "error",
                "error": "course_not_published",
            })
            return Response(
                {'error': 'Невозможно записать на неопубликованный курс.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=user,
            course=course,
            defaults={'status': CourseEnrollment.Status.ACTIVE}
        )
        
        log_line("courses", "DEBUG", "enroll_user", "ENROLL_USER", "DECISION", {
            "created": created,
            "enrollment_id": enrollment.id,
        })
        
        if not created:
            log_line("courses", "WARN", "enroll_user", "ENROLL_USER", "ERROR", {
                "reason": "already_enrolled",
                "user_id": user.id,
                "course_id": course.id,
            })
            log_line("courses", "DEBUG", "enroll_user", "ENROLL_USER", "EXIT", {
                "result": "error",
                "error": "already_enrolled",
            })
            return Response(
                {'error': 'Пользователь уже записан на этот курс.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        log_line("courses", "INFO", "enroll_user", "ENROLL_USER", "STATE_CHANGE", {
            "action": "user_enrolled_by_admin",
            "user_id": user.id,
            "course_id": course.id,
            "enrollment_id": enrollment.id,
            "admin_user_id": request.user.id,
        })
        log_line("courses", "DEBUG", "enroll_user", "ENROLL_USER", "EXIT", {
            "result": "success",
            "enrollment_id": enrollment.id,
        })
        return Response(
            CourseEnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )
    # [END_ENROLL_USER]


# [END_ENROLLMENT_VIEWSET]


# === END_CHUNK: COURSE_VIEWS_V1 ===
