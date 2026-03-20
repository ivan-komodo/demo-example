"""Progress serializers."""

from rest_framework import serializers

from .models import UserProgress


class UserProgressSerializer(serializers.ModelSerializer):
    """Serializer for UserProgress model."""
    
    module_title = serializers.CharField(source='module.title', read_only=True)
    course_title = serializers.CharField(source='module.course.title', read_only=True)
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'user', 'module', 'module_title', 'course_title',
            'status', 'completed_at', 'score'
        ]
        read_only_fields = ['id', 'user', 'completed_at']


class CourseProgressSerializer(serializers.Serializer):
    """Serializer for course progress summary."""
    
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    total_modules = serializers.IntegerField()
    completed_modules = serializers.IntegerField()
    in_progress_modules = serializers.IntegerField()
    not_started_modules = serializers.IntegerField()
    progress_percentage = serializers.FloatField()


class UpdateProgressSerializer(serializers.Serializer):
    """Serializer for updating progress."""
    
    module_id = serializers.IntegerField()
    status = serializers.CharField()