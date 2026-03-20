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
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return CourseCreateSerializer
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = Course.objects.prefetch_related('modules')
        
        if self.request.user.is_admin:
            return queryset
        
        # Non-admins can only see published courses
        return queryset.filter(status='published')
    
    def perform_create(self, serializer):
        """Create a new course."""
        serializer.save()
    
    def perform_update(self, serializer):
        """Update a course."""
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete a course."""
        instance.delete()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def publish(self, request, pk=None):
        """Publish a course."""
        course = self.get_object()
        course.status = Course.Status.PUBLISHED
        course.save(update_fields=['status'])
        return Response({'message': 'Курс опубликован.'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def archive(self, request, pk=None):
        """Archive a course."""
        course = self.get_object()
        course.status = Course.Status.ARCHIVED
        course.save(update_fields=['status'])
        return Response({'message': 'Курс архивирован.'})
    
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
    
    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        """Return courses the current user is enrolled in."""
        enrollments = CourseEnrollment.objects.filter(
            user=request.user,
            status=CourseEnrollment.Status.ACTIVE
        ).select_related('course')
        
        serializer = CourseEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)


class ModuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Module model.
    
    Provides CRUD operations for modules.
    Only admins can create, update, or delete modules.
    """
    
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ModuleCreateSerializer
        return ModuleSerializer
    
    def get_queryset(self):
        """Filter modules by course."""
        queryset = Module.objects.select_related('course')
        course_id = self.request.query_params.get('course_id')
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create a new module."""
        serializer.save()


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
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = CourseEnrollment.objects.select_related('user', 'course')
        
        if self.request.user.is_admin:
            return queryset
        
        # Non-admins can only see their own enrollments
        return queryset.filter(user=self.request.user)
    
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