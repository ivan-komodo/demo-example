"""Booking serializers."""

from rest_framework import serializers

from .models import Booking, Resource


class ResourceSerializer(serializers.ModelSerializer):
    """Serializer for Resource model."""
    
    class Meta:
        model = Resource
        fields = ['id', 'name', 'type', 'description', 'capacity', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


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


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings."""
    
    class Meta:
        model = Booking
        fields = [
            'resource', 'course', 'title', 'description',
            'start_time', 'end_time'
        ]
    
    def validate(self, attrs):
        """Validate booking for conflicts."""
        booking = Booking(**attrs)
        if booking.check_conflict():
            raise serializers.ValidationError(
                'Ресурс уже забронирован на это время.'
            )
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Booking.objects.create(**validated_data)