"""
Course serializers for LMS System.
"""

from rest_framework import serializers

from .models import Course, CourseEnrollment, Module


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


class ModuleListSerializer(serializers.ModelSerializer):
    """Serializer for listing modules without content."""
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'content_type', 'order_num']


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


class CourseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating courses."""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'status']


class ModuleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating modules."""
    
    class Meta:
        model = Module
        fields = [
            'course', 'title', 'content_type',
            'content_text', 'content_url', 'content_file'
        ]


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


class EnrollUserSerializer(serializers.Serializer):
    """Serializer for enrolling user in a course."""
    
    user_id = serializers.IntegerField()
    course_id = serializers.IntegerField()


class UserCourseProgressSerializer(serializers.Serializer):
    """Serializer for user progress on a course."""
    
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    total_modules = serializers.IntegerField()
    completed_modules = serializers.IntegerField()
    progress_percentage = serializers.FloatField()
    status = serializers.CharField()