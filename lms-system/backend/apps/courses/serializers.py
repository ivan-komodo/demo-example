"""
Course serializers for LMS System.
"""

from rest_framework import serializers

from .models import Course, CourseEnrollment, Module


# === CHUNK: COURSE_SERIALIZERS_V1 [COURSES] ===
# Описание: Сериализаторы для курсов, модулей и записей на курсы.
# Dependencies: COURSE_MODELS_V1


# [START_MODULE_SERIALIZER]
# ANCHOR: MODULE_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - предоставляет сериализацию/десериализацию модели Module
# PURPOSE: Полный сериализатор для модели Module.
class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for Module model."""
    
    class Meta:
        model = Module
        fields = [
            'id', 'course', 'title', 'content_type',
            'content_text', 'content_url', 'content_file',
            'order_num', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_num', 'created_at', 'updated_at']
# [END_MODULE_SERIALIZER]


# [START_MODULE_LIST_SERIALIZER]
# ANCHOR: MODULE_LIST_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - предоставляет сокращённую сериализацию модуля для списков
# PURPOSE: Краткий сериализатор модуля без контента для списков.
class ModuleListSerializer(serializers.ModelSerializer):
    """Serializer for listing modules without content."""
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'content_type', 'order_num']
# [END_MODULE_LIST_SERIALIZER]


# [START_COURSE_SERIALIZER]
# ANCHOR: COURSE_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - предоставляет сериализацию/десериализацию модели Course
# - включает вложенные модули и вычисляемые поля
# PURPOSE: Полный сериализатор для модели Course с модулями.
class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model."""
    
    modules = ModuleListSerializer(many=True, read_only=True)
    modules_count = serializers.ReadOnlyField()
    enrolled_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'status',
            'modules', 'modules_count', 'enrolled_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
# [END_COURSE_SERIALIZER]


# [START_COURSE_LIST_SERIALIZER]
# ANCHOR: COURSE_LIST_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - предоставляет сокращённую сериализацию курса для списков
# PURPOSE: Краткий сериализатор курса для списков без вложенных модулей.
class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for listing courses."""
    
    modules_count = serializers.ReadOnlyField()
    enrolled_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'status',
            'modules_count', 'enrolled_count', 'created_at'
        ]
# [END_COURSE_LIST_SERIALIZER]


# [START_COURSE_CREATE_SERIALIZER]
# ANCHOR: COURSE_CREATE_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - предоставляет сериализацию для создания курса
# PURPOSE: Сериализатор для создания новых курсов.
class CourseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating courses."""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'status']
# [END_COURSE_CREATE_SERIALIZER]


# [START_MODULE_CREATE_SERIALIZER]
# ANCHOR: MODULE_CREATE_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - предоставляет сериализацию для создания модуля
# PURPOSE: Сериализатор для создания новых модулей.
class ModuleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating modules."""
    
    class Meta:
        model = Module
        fields = [
            'course', 'title', 'content_type',
            'content_text', 'content_url', 'content_file'
        ]
# [END_MODULE_CREATE_SERIALIZER]


# [START_COURSE_ENROLLMENT_SERIALIZER]
# ANCHOR: COURSE_ENROLLMENT_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - предоставляет сериализацию/десериализацию модели CourseEnrollment
# - включает вычисляемые поля для прогресса
# PURPOSE: Сериализатор для записей пользователей на курсы.
class CourseEnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for CourseEnrollment model."""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'user', 'course', 'course_title', 'user_email',
            'enrolled_at', 'status', 'completed_at', 'progress_percentage'
        ]
        read_only_fields = ['id', 'enrolled_at', 'completed_at']
# [END_COURSE_ENROLLMENT_SERIALIZER]


# [START_ENROLL_USER_SERIALIZER]
# ANCHOR: ENROLL_USER_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - валидирует user_id и course_id
# PURPOSE: Сериализатор для записи пользователя на курс по ID.
class EnrollUserSerializer(serializers.Serializer):
    """Serializer for enrolling user in a course."""
    
    user_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
# [END_ENROLL_USER_SERIALIZER]


# [START_USER_COURSE_PROGRESS_SERIALIZER]
# ANCHOR: USER_COURSE_PROGRESS_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - предоставляет структуру для отображения прогресса пользователя
# PURPOSE: Сериализатор для отображения прогресса пользователя по курсу.
class UserCourseProgressSerializer(serializers.Serializer):
    """Serializer for user progress on a course."""
    
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    total_modules = serializers.IntegerField()
    completed_modules = serializers.IntegerField()
    progress_percentage = serializers.FloatField()
    status = serializers.CharField()
# [END_USER_COURSE_PROGRESS_SERIALIZER]


# === END_CHUNK: COURSE_SERIALIZERS_V1 ===