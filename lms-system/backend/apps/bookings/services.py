"""Booking services."""

from django.contrib.auth import get_user_model

from .models import Booking, Resource

User = get_user_model()


# === CHUNK: BOOKING_SERVICES_V1 [BOOKINGS] ===
# Описание: Бизнес-логика для управления бронированиями.
# Dependencies: BOOKING_MODELS_V1


# [START_BOOKING_SERVICE_CLASS]
# ANCHOR: BOOKING_SERVICE_CLASS
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет методы для проверки доступности и получения бронирований
# PURPOSE: Сервисный класс для инкапсуляции бизнес-логики бронирований.
class BookingService:
    """Service for booking management."""
    
    # [START_CHECK_AVAILABILITY]
    # ANCHOR: CHECK_AVAILABILITY
    # @PreConditions:
    # - resource существует
    # - start_time и end_time заданы
    # @PostConditions:
    # - возвращает True если ресурс доступен, иначе False
    # PURPOSE: Проверка доступности ресурса для бронирования на указанный период.
    @staticmethod
    def check_availability(resource: Resource, start_time, end_time, exclude_booking=None) -> bool:
        """Check if resource is available for booking."""
        queryset = Booking.objects.filter(
            resource=resource,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        )
        
        if exclude_booking:
            queryset = queryset.exclude(pk=exclude_booking.pk)
        
        return not queryset.exists()
    # [END_CHECK_AVAILABILITY]
    
    # [START_GET_USER_BOOKINGS]
    # ANCHOR: GET_USER_BOOKINGS
    # @PreConditions:
    # - user аутентифицирован
    # @PostConditions:
    # - возвращает QuerySet с бронированиями пользователя
    # PURPOSE: Получение всех бронирований указанного пользователя.
    @staticmethod
    def get_user_bookings(user: User):
        """Get all bookings for a user."""
        return Booking.objects.filter(user=user).select_related('resource', 'course')
    # [END_GET_USER_BOOKINGS]
    
    # [START_GET_RESOURCE_BOOKINGS]
    # ANCHOR: GET_RESOURCE_BOOKINGS
    # @PreConditions:
    # - resource существует
    # @PostConditions:
    # - возвращает QuerySet с бронированиями ресурса
    # PURPOSE: Получение всех бронирований указанного ресурса.
    @staticmethod
    def get_resource_bookings(resource: Resource):
        """Get all bookings for a resource."""
        return Booking.objects.filter(resource=resource).select_related('user', 'course')
    # [END_GET_RESOURCE_BOOKINGS]


# [END_BOOKING_SERVICE_CLASS]


# === END_CHUNK: BOOKING_SERVICES_V1 ===