"""Booking views."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsAdminUser

from .models import Booking, Resource
from .serializers import BookingCreateSerializer, BookingSerializer, ResourceSerializer


# === CHUNK: BOOKING_VIEWS_V1 [BOOKINGS] ===
# Описание: ViewSet для управления ресурсами и бронированиями.
# Dependencies: BOOKING_MODELS_V1, BOOKING_SERIALIZERS_V1


# [START_RESOURCE_VIEWSET]
# ANCHOR: RESOURCE_VIEWSET
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет CRUD операции для ресурсов
# PURPOSE: ViewSet для управления ресурсами (аудитории, тренеры, оборудование).
class ResourceViewSet(viewsets.ModelViewSet):
    """ViewSet for Resource model."""
    
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]
# [END_RESOURCE_VIEWSET]


# [START_BOOKING_VIEWSET]
# ANCHOR: BOOKING_VIEWSET
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет CRUD операции для бронирований
# - предоставляет action для отмены бронирования
# PURPOSE: ViewSet для управления бронированиями ресурсов.
class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for Booking model."""
    
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    # [START_GET_SERIALIZER_CLASS]
    # ANCHOR: GET_SERIALIZER_CLASS
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает BookingCreateSerializer для создания, иначе BookingSerializer
    # PURPOSE: Выбор сериализатора в зависимости от действия.
    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer
    # [END_GET_SERIALIZER_CLASS]
    
    # [START_GET_BOOKING_QUERYSET]
    # ANCHOR: GET_BOOKING_QUERYSET
    # @PreConditions:
    # - request.user аутентифицирован
    # @PostConditions:
    # - для админов возвращает все бронирования
    # - для обычных пользователей — только их бронирования
    # - фильтрует по resource_id если передан
    # PURPOSE: Фильтрация бронирований по пользователю и ресурсу.
    def get_queryset(self):
        queryset = Booking.objects.select_related('resource', 'user', 'course')
        
        if not self.request.user.is_admin:
            queryset = queryset.filter(user=self.request.user)
        
        resource_id = self.request.query_params.get('resource_id')
        if resource_id:
            queryset = queryset.filter(resource_id=resource_id)
        
        return queryset
    # [END_GET_BOOKING_QUERYSET]
    
    # [START_PERFORM_CREATE_BOOKING]
    # ANCHOR: PERFORM_CREATE_BOOKING
    # @PreConditions:
    # - serializer валиден
    # - request.user аутентифицирован
    # @PostConditions:
    # - создаёт бронирование с текущим пользователем
    # PURPOSE: Автоматическое связывание бронирования с текущим пользователем.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    # [END_PERFORM_CREATE_BOOKING]
    
    # [START_CANCEL_BOOKING]
    # ANCHOR: CANCEL_BOOKING
    # @PreConditions:
    # - request.user аутентифицирован
    # - бронирование существует
    # @PostConditions:
    # - статус бронирования изменён на CANCELLED
    # PURPOSE: Отмена бронирования.
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        booking = self.get_object()
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=['status'])
        return Response({'message': 'Бронирование отменено.'})
    # [END_CANCEL_BOOKING]


# [END_BOOKING_VIEWSET]


# === END_CHUNK: BOOKING_VIEWS_V1 ===