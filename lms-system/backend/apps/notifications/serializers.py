"""Notification serializers."""

from rest_framework import serializers

from .models import Notification


# === CHUNK: NOTIFICATION_SERIALIZERS_V1 [NOTIFICATIONS] ===
# Описание: Сериализаторы для уведомлений.
# Dependencies: NOTIFICATION_MODELS_V1


# [START_NOTIFICATION_SERIALIZER]
# ANCHOR: NOTIFICATION_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - сериализует все поля модели Notification
# PURPOSE: Сериализатор для чтения уведомлений.
class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model (read operations)."""
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'type', 'title', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
# [END_NOTIFICATION_SERIALIZER]


# [START_NOTIFICATION_CREATE_SERIALIZER]
# ANCHOR: NOTIFICATION_CREATE_SERIALIZER
# @PreConditions:
# - user передан в context или validated_data
# @PostConditions:
# - создаёт уведомление для указанного пользователя
# PURPOSE: Сериализатор для создания уведомлений.
class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications."""
    
    class Meta:
        model = Notification
        fields = ['user', 'type', 'title', 'message']
    
    # [START_NOTIFICATION_CREATE_CREATE]
    # ANCHOR: NOTIFICATION_CREATE_CREATE
    # @PreConditions:
    # - validated_data содержит user, type, title, message
    # @PostConditions:
    # - создаёт и возвращает экземпляр Notification
    # PURPOSE: Создание уведомления с валидированными данными.
    def create(self, validated_data):
        return Notification.objects.create(**validated_data)
    # [END_NOTIFICATION_CREATE_CREATE]


# [END_NOTIFICATION_CREATE_SERIALIZER]


# [START_MARK_AS_READ_SERIALIZER]
# ANCHOR: MARK_AS_READ_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - валидирует список ID уведомлений
# PURPOSE: Сериализатор для массовой отметки уведомлений как прочитанные.
class MarkAsReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read."""
    
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )
# [END_MARK_AS_READ_SERIALIZER]


# === END_CHUNK: NOTIFICATION_SERIALIZERS_V1 ===