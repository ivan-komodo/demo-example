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
# ANCHOR: COURSE_VIEWSET
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет CRUD операции для курсов
# - администраторы могут создавать, обновлять, удалять курсы
# PURPOSE: ViewSet для управления курсами с разграничением прав доступа.
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
    # ANCHOR: GET_SERIALIZER_CLASS_COURSE
    # @PreConditions:
    # - request.user аутентифицирован
    # @PostConditions:
    # - возвращает CourseCreateSerializer для create
    # - возвращает CourseListSerializer для list
    # - возвращает CourseSerializer для остальных действий
    # PURPOSE: Выбор сериализатора в зависимости от действия.
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return CourseCreateSerializer
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer
    # [END_GET_SERIALIZER_CLASS_COURSE]
    
    # [START_GET_QUERYSET_COURSE]
    # ANCHOR: GET_QUERYSET_COURSE
    # @PreConditions:
    # - request.user аутентифицирован
    # @PostConditions:
    # - для администраторов возвращает все курсы
    # - для остальных — только опубликованные
    # PURPOSE: Фильтрация queryset в зависимости от роли пользователя.
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = Course.objects.prefetch_related('modules')
        
        if self.request.user.is_admin:
            return queryset
        
        # Non-admins can only see published courses
        return queryset.filter(status='published')
    # [END_GET_QUERYSET_COURSE]
    
    # [START_PERFORM_CREATE_COURSE]
    # ANCHOR: PERFORM_CREATE_COURSE
    # @PreConditions:
    # - serializer валиден
    # - request.user — администратор
    # @PostConditions:
    # - курс создан и сохранён в БД
    # PURPOSE: Создание нового курса.
    def perform_create(self, serializer):
        """Create a new course."""
        serializer.save()
    # [END_PERFORM_CREATE_COURSE]
    
    # [START_PERFORM_UPDATE_COURSE]
    # ANCHOR: PERFORM_UPDATE_COURSE
    # @PreConditions:
    # - serializer валиден
    # - request.user — администратор
    # @PostConditions:
    # - курс обновлён в БД
    # PURPOSE: Обновление существующего курса.
    def perform_update(self, serializer):
        """Update a course."""
        serializer.save()
    # [END_PERFORM_UPDATE_COURSE]
    
    # [START_PERFORM_DESTROY_COURSE]
    # ANCHOR: PERFORM_DESTROY_COURSE
    # @PreConditions:
    # - instance существует
    # - request.user — администратор
    # @PostConditions:
    # - курс удалён из БД
    # PURPOSE: Удаление курса.
    def perform_destroy(self, instance):
        """Delete a course."""
        instance.delete()
    # [END_PERFORM_DESTROY_COURSE]
    
    # [START_PUBLISH_COURSE]
    # ANCHOR: PUBLISH_COURSE
    # @PreConditions:
    # - курс существует
    # - request.user — администратор
    # @PostConditions:
    # - статус курса изменён на PUBLISHED
    # - возвращён ответ с сообщением об успехе
    # PURPOSE: Публикация курса (смена статуса на published).
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def publish(self, request, pk=None):
        """Publish a course."""
        course = self.get_object()
        course.status = Course.Status.PUBLISHED
        course.save(update_fields=['status'])
        return Response({'message': 'Курс опубликован.'})
    # [END_PUBLISH_COURSE]
    
    # [START_ARCHIVE_COURSE]
    # ANCHOR: ARCHIVE_COURSE
    # @PreConditions:
    # - курс существует
    # - request.user — администратор
    # @PostConditions:
    # - статус курса изменён на ARCHIVED
    # - возвращён ответ с сообщением об успехе
    # PURPOSE: Архивирование курса (смена статуса на archived).
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def archive(self, request, pk=None):
        """Archive a course."""
        course = self.get_object()
        course.status = Course.Status.ARCHIVED
        course.save(update_fields=['status'])
        return Response({'message': 'Курс архивирован.'})
    # [END_ARCHIVE_COURSE]
    
    # [START_ENROLL_SELF]
    # ANCHOR: ENROLL_SELF
    # @PreConditions:
    # - курс существует и опубликован
    # - request.user аутентифицирован
    # @PostConditions:
    # - при успехе создаётся запись CourseEnrollment
    # - при повторной записи возвращается ошибка
    # PURPOSE: Запись текущего пользователя на курс.
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """Enroll current user in the course."""
        course = self.get_object()
        
        if course.status != Course.Status.PUBLISHED:
            return Response(
                {'error': 'Невозможно записаться на неопубликованный курс.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'status': CourseEnrollment.Status.ACTIVE}
        )
        
        if not created:
            return Response(
                {'error': 'Вы уже записаны на этот курс.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            CourseEnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )
    # [END_ENROLL_SELF]
    
    # [START_MY_COURSES]
    # ANCHOR: MY_COURSES
    # @PreConditions:
    # - request.user аутентифицирован
    # @PostConditions:
    # - возвращает список активных записей пользователя на курсы
    # PURPOSE: Получение курсов, на которые записан текущий пользователь.
    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        """Return courses the current user is enrolled in."""
        enrollments = CourseEnrollment.objects.filter(
            user=request.user,
            status=CourseEnrollment.Status.ACTIVE
        ).select_related('course')
        
        serializer = CourseEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    # [END_MY_COURSES]


# [END_COURSE_VIEWSET]


# [START_MODULE_VIEWSET]
# ANCHOR: MODULE_VIEWSET
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет CRUD операции для модулей
# PURPOSE: ViewSet для управления модулями курсов.
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
    # ANCHOR: GET_SERIALIZER_CLASS_MODULE
    # @PreConditions:
    # - request.user аутентифицирован
    # @PostConditions:
    # - возвращает ModuleCreateSerializer для create
    # - возвращает ModuleSerializer для остальных действий
    # PURPOSE: Выбор сериализатора в зависимости от действия.
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ModuleCreateSerializer
        return ModuleSerializer
    # [END_GET_SERIALIZER_CLASS_MODULE]
    
    # [START_GET_QUERYSET_MODULE]
    # ANCHOR: GET_QUERYSET_MODULE
    # @PreConditions:
    # - request.user аутентифицирован
    # @PostConditions:
    # - при наличии course_id фильтрует модули по курсу
    # PURPOSE: Фильтрация модулей по курсу через query-параметры.
    def get_queryset(self):
        """Filter modules by course."""
        queryset = Module.objects.select_related('course')
        course_id = self.request.query_params.get('course_id')
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        return queryset
    # [END_GET_QUERYSET_MODULE]
    
    # [START_PERFORM_CREATE_MODULE]
    # ANCHOR: PERFORM_CREATE_MODULE
    # @PreConditions:
    # - serializer валиден
    # - request.user — администратор
    # @PostConditions:
    # - модуль создан и сохранён в БД
    # PURPOSE: Создание нового модуля.
    def perform_create(self, serializer):
        """Create a new module."""
        serializer.save()
    # [END_PERFORM_CREATE_MODULE]


# [END_MODULE_VIEWSET]


# [START_ENROLLMENT_VIEWSET]
# ANCHOR: ENROLLMENT_VIEWSET
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет операции для управления записями на курсы
# PURPOSE: ViewSet для управления записями пользователей на курсы.
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
    # ANCHOR: GET_QUERYSET_ENROLLMENT
    # @PreConditions:
    # - request.user аутентифицирован
    # @PostConditions:
    # - для администраторов возвращает все записи
    # - для остальных — только свои записи
    # PURPOSE: Фильтрация записей в зависимости от роли пользователя.
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = CourseEnrollment.objects.select_related('user', 'course')
        
        if self.request.user.is_admin:
            return queryset
        
        # Non-admins can only see their own enrollments
        return queryset.filter(user=self.request.user)
    # [END_GET_QUERYSET_ENROLLMENT]
    
    # [START_ENROLL_USER]
    # ANCHOR: ENROLL_USER
    # @PreConditions:
    # - request.user — администратор
    # - request.data содержит user_id и course_id
    # @PostConditions:
    # - при успехе создаётся запись CourseEnrollment для указанного пользователя
    # - при ошибке возвращается соответствующий ответ
    # PURPOSE: Запись конкретного пользователя на курс (для администраторов).
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def enroll_user(self, request):
        """Enroll a specific user in a course."""
        serializer = EnrollUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        course_id = serializer.validated_data['course_id']
        
        try:
            user = User.objects.get(id=user_id)
            course = Course.objects.get(id=course_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Course.DoesNotExist:
            return Response(
                {'error': 'Курс не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if course.status != Course.Status.PUBLISHED:
            return Response(
                {'error': 'Невозможно записать на неопубликованный курс.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=user,
            course=course,
            defaults={'status': CourseEnrollment.Status.ACTIVE}
        )
        
        if not created:
            return Response(
                {'error': 'Пользователь уже записан на этот курс.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            CourseEnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )
    # [END_ENROLL_USER]


# [END_ENROLLMENT_VIEWSET]


# === END_CHUNK: COURSE_VIEWS_V1 ===