"""Booking serializers."""

from rest_framework import serializers

from .models import Booking, Resource


# === CHUNK: BOOKING_SERIALIZERS_V1 [BOOKINGS] ===
# Описание: Сериализаторы для ресурсов и бронирований.
# Dependencies: BOOKING_MODELS_V1


# [START_RESOURCE_SERIALIZER]
# ANCHOR: RESOURCE_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для модели Resource
# PURPOSE: Сериализатор для ресурсов (аудитории, тренеры, оборудование).
class ResourceSerializer(serializers.ModelSerializer):
    """Serializer for Resource model."""
    
    class Meta:
        model = Resource
        fields = ['id', 'name', 'type', 'description', 'capacity', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
# [END_RESOURCE_SERIALIZER]


# [START_BOOKING_SERIALIZER]
# ANCHOR: BOOKING_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для модели Booking с дополнительными полями
# PURPOSE: Сериализатор для чтения бронирований.
class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model."""
    
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'resource', 'resource_name', 'user', 'user_email',
            'course', 'course_title', 'title', 'description',
            'start_time', 'end_time', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
# [END_BOOKING_SERIALIZER]


# [START_BOOKING_CREATE_SERIALIZER]
# ANCHOR: BOOKING_CREATE_SERIALIZER
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - создаёт сериализатор для создания бронирований с валидацией конфликтов
# PURPOSE: Сериализатор для создания бронирований.
class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings."""
    
    class Meta:
        model = Booking
        fields = [
            'resource', 'course', 'title', 'description',
            'start_time', 'end_time'
        ]
    
    # [START_VALIDATE_BOOKING]
    # ANCHOR: VALIDATE_BOOKING
    # @PreConditions:
    # - attrs содержит resource, start_time, end_time
    # @PostConditions:
    # - при конфликте выбрасывает ValidationError
    # PURPOSE: Валидация бронирования на конфликты с существующими.
    def validate(self, attrs):
        """Validate booking for conflicts."""
        booking = Booking(**attrs)
        if booking.check_conflict():
            raise serializers.ValidationError(
                'Ресурс уже забронирован на это время.'
            )
        return attrs
    # [END_VALIDATE_BOOKING]
    
    # [START_CREATE_BOOKING]
    # ANCHOR: CREATE_BOOKING
    # @PreConditions:
    # - validated_data валидирован
    # - request.user аутентифицирован
    # @PostConditions:
    # - создаёт бронирование с текущим пользователем
    # PURPOSE: Создание бронирования с автоматическим связыванием с пользователем.
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Booking.objects.create(**validated_data)
    # [END_CREATE_BOOKING]


# [END_BOOKING_CREATE_SERIALIZER]


# === END_CHUNK: BOOKING_SERIALIZERS_V1 ===