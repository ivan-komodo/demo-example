"""Progress serializers."""

from rest_framework import serializers

from .models import UserProgress


# === CHUNK: PROGRESS_SERIALIZERS_V1 [PROGRESS] ===
# Описание: Сериализаторы для прогресса пользователей.
# Dependencies: PROGRESS_MODELS_V1


# [START_USER_PROGRESS_SERIALIZER]
# ANCHOR: USER_PROGRESS_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для модели UserProgress
# PURPOSE: Сериализатор для прогресса пользователя по модулю.
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
# [END_USER_PROGRESS_SERIALIZER]


# [START_COURSE_PROGRESS_SERIALIZER]
# ANCHOR: COURSE_PROGRESS_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для сводки прогресса по курсу
# PURPOSE: Сериализатор для сводки прогресса по курсу.
class CourseProgressSerializer(serializers.Serializer):
    """Serializer for course progress summary."""
    
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    total_modules = serializers.IntegerField()
    completed_modules = serializers.IntegerField()
    in_progress_modules = serializers.IntegerField()
    not_started_modules = serializers.IntegerField()
    progress_percentage = serializers.FloatField()
# [END_COURSE_PROGRESS_SERIALIZER]


# [START_UPDATE_PROGRESS_SERIALIZER]
# ANCHOR: UPDATE_PROGRESS_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для обновления статуса прогресса
# PURPOSE: Сериализатор для обновления статуса прогресса по модулю.
class UpdateProgressSerializer(serializers.Serializer):
    """Serializer for updating progress."""
    
    module_id = serializers.IntegerField()
    status = serializers.CharField()
# [END_UPDATE_PROGRESS_SERIALIZER]


# === END_CHUNK: PROGRESS_SERIALIZERS_V1 ===