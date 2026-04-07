"""Booking views."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsAdminUser
from core.utils import log_line

from .models import Booking, Resource
from .serializers import BookingCreateSerializer, BookingSerializer, ResourceSerializer


# === CHUNK: BOOKING_VIEWS_V1 [BOOKINGS] ===
# Описание: ViewSet для управления ресурсами и бронированиями.
# Dependencies: BOOKING_MODELS_V1, BOOKING_SERIALIZERS_V1


# [START_RESOURCE_VIEWSET]
"""
ANCHOR: RESOURCE_VIEWSET
PURPOSE: ViewSet для управления ресурсами (аудитории, тренеры, оборудование).

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет CRUD операции для ресурсов через REST API
- требует аутентификации для всех операций

@Invariants:
- permission_classes всегда [IsAuthenticated]
- queryset возвращает все активные и неактивные ресурсы

@SideEffects:
- чтение и запись БД через ModelViewSet
- HTTP responses клиентам

@ForbiddenChanges:
- базовые CRUD операции (наследуются от ModelViewSet)
"""
class ResourceViewSet(viewsets.ModelViewSet):
    """ViewSet for Resource model."""
    
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]
# [END_RESOURCE_VIEWSET]


# [START_BOOKING_VIEWSET]
"""
ANCHOR: BOOKING_VIEWSET
PURPOSE: ViewSet для управления бронированиями ресурсов.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет CRUD операции для бронирований через REST API
- предоставляет action для отмены бронирования
- требует аутентификации для всех операций
- автоматически связывает бронирование с текущим пользователем

@Invariants:
- permission_classes всегда [IsAuthenticated]
- обычные пользователи видят только свои бронирования
- админы видят все бронирования

@SideEffects:
- чтение и запись БД через ModelViewSet
- HTTP responses клиентам

@ForbiddenChanges:
- логика фильтрации по is_admin в get_queryset
- автоматическое связывание с user в perform_create
"""
class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for Booking model."""
    
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    # [START_GET_SERIALIZER_CLASS]
    """
    ANCHOR: GET_SERIALIZER_CLASS
    PURPOSE: Выбор сериализатора в зависимости от действия.

    @PreConditions:
    - self.action определён Django REST Framework

    @PostConditions:
    - для action='create' возвращает BookingCreateSerializer
    - для других actions возвращает BookingSerializer

    @Invariants:
    - всегда возвращает класс сериализатора (не None)

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - использование BookingCreateSerializer для create (валидация при создании)
    """
    def get_serializer_class(self):
        log_line("bookings", "DEBUG", "BookingViewSet.get_serializer_class", "GET_SERIALIZER_CLASS", "ENTRY", {
            "action": self.action,
        })
        
        if self.action == 'create':
            log_line("bookings", "DEBUG", "BookingViewSet.get_serializer_class", "GET_SERIALIZER_CLASS", "BRANCH", {
                "branch": "create_action",
                "serializer": "BookingCreateSerializer",
            })
            result = BookingCreateSerializer
        else:
            log_line("bookings", "DEBUG", "BookingViewSet.get_serializer_class", "GET_SERIALIZER_CLASS", "BRANCH", {
                "branch": "other_action",
                "serializer": "BookingSerializer",
            })
            result = BookingSerializer
        
        log_line("bookings", "DEBUG", "BookingViewSet.get_serializer_class", "GET_SERIALIZER_CLASS", "EXIT", {
            "serializer": result.__name__,
        })
        return result
    # [END_GET_SERIALIZER_CLASS]
    
    # [START_GET_BOOKING_QUERYSET]
    """
    ANCHOR: GET_BOOKING_QUERYSET
    PURPOSE: Фильтрация бронирований по пользователю и ресурсу.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - для админов возвращает все бронирования
    - для обычных пользователей — только их бронирования
    - фильтрует по resource_id если передан в query_params
    - возвращает QuerySet с select_related для оптимизации

    @Invariants:
    - всегда возвращает QuerySet
    - запрос всегда оптимизирован через select_related

    @SideEffects:
    - нет побочных эффектов (только чтение БД)

    @ForbiddenChanges:
    - логика фильтрации по is_admin
    - select_related для resource, user, course
    """
    def get_queryset(self):
        log_line("bookings", "DEBUG", "BookingViewSet.get_queryset", "GET_BOOKING_QUERYSET", "ENTRY", {
            "user_id": self.request.user.pk,
            "is_admin": self.request.user.is_admin,
        })
        
        queryset = Booking.objects.select_related('resource', 'user', 'course')
        
        if not self.request.user.is_admin:
            log_line("bookings", "DEBUG", "BookingViewSet.get_queryset", "GET_BOOKING_QUERYSET", "BRANCH", {
                "branch": "non_admin_user",
                "filter": "user_bookings_only",
            })
            queryset = queryset.filter(user=self.request.user)
        else:
            log_line("bookings", "DEBUG", "BookingViewSet.get_queryset", "GET_BOOKING_QUERYSET", "BRANCH", {
                "branch": "admin_user",
                "filter": "all_bookings",
            })
        
        resource_id = self.request.query_params.get('resource_id')
        if resource_id:
            log_line("bookings", "DEBUG", "BookingViewSet.get_queryset", "GET_BOOKING_QUERYSET", "DECISION", {
                "decision": "filter_by_resource",
                "resource_id": resource_id,
            })
            queryset = queryset.filter(resource_id=resource_id)
        
        log_line("bookings", "DEBUG", "BookingViewSet.get_queryset", "GET_BOOKING_QUERYSET", "EXIT", {
            "result": "queryset",
            "user_id": self.request.user.pk,
        })
        return queryset
    # [END_GET_BOOKING_QUERYSET]
    
    # [START_PERFORM_CREATE_BOOKING]
    """
    ANCHOR: PERFORM_CREATE_BOOKING
    PURPOSE: Автоматическое связывание бронирования с текущим пользователем.

    @PreConditions:
    - serializer валиден
    - request.user аутентифицирован

    @PostConditions:
    - создаёт бронирование с user=request.user
    - сохраняет бронирование в БД

    @Invariants:
    - пользователь всегда берётся из request.user
    - нельзя создать бронирование от имени другого пользователя

    @SideEffects:
    - запись в БД (создание Booking)
    - отправка HTTP response

    @ForbiddenChanges:
    - автоматическое связывание с request.user
    """
    def perform_create(self, serializer):
        log_line("bookings", "DEBUG", "BookingViewSet.perform_create", "PERFORM_CREATE_BOOKING", "ENTRY", {
            "user_id": self.request.user.pk,
        })
        
        booking = serializer.save(user=self.request.user)
        
        log_line("bookings", "INFO", "BookingViewSet.perform_create", "PERFORM_CREATE_BOOKING", "STATE_CHANGE", {
            "entity": "booking",
            "id": booking.pk,
            "action": "created",
            "user_id": self.request.user.pk,
            "resource_id": booking.resource_id,
        })
        
        log_line("bookings", "DEBUG", "BookingViewSet.perform_create", "PERFORM_CREATE_BOOKING", "EXIT", {
            "result": "booking_created",
            "booking_id": booking.pk,
        })
    # [END_PERFORM_CREATE_BOOKING]
    
    # [START_CANCEL_BOOKING]
    """
    ANCHOR: CANCEL_BOOKING
    PURPOSE: Отмена бронирования.

    @PreConditions:
    - request.user аутентифицирован
    - бронирование существует (pk валиден)
    - пользователь имеет права на это бронирование (проверяется get_object)

    @PostConditions:
    - статус бронирования изменён на CANCELLED
    - возвращает HTTP 200 с сообщением об успехе

    @Invariants:
    - изменяется только поле status
    - используется update_fields для оптимизации

    @SideEffects:
    - запись в БД (изменение status)
    - отправка HTTP response

    @ForbiddenChanges:
    - статус всегда меняется на CANCELLED (не удаляется)
    - update_fields=['status'] для оптимизации
    """
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        log_line("bookings", "DEBUG", "BookingViewSet.cancel", "CANCEL_BOOKING", "ENTRY", {
            "user_id": request.user.pk,
            "booking_id": pk,
        })
        
        booking = self.get_object()
        old_status = booking.status
        
        log_line("bookings", "DEBUG", "BookingViewSet.cancel", "CANCEL_BOOKING", "BRANCH", {
            "branch": "status_change",
            "old_status": old_status,
            "new_status": Booking.Status.CANCELLED,
        })
        
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=['status'])
        
        log_line("bookings", "INFO", "BookingViewSet.cancel", "CANCEL_BOOKING", "STATE_CHANGE", {
            "entity": "booking",
            "id": booking.pk,
            "action": "cancelled",
            "old_status": old_status,
            "new_status": Booking.Status.CANCELLED,
            "user_id": request.user.pk,
        })
        
        log_line("bookings", "DEBUG", "BookingViewSet.cancel", "CANCEL_BOOKING", "EXIT", {
            "result": "booking_cancelled",
            "booking_id": booking.pk,
        })
        return Response({'message': 'Бронирование отменено.'})
    # [END_CANCEL_BOOKING]


# [END_BOOKING_VIEWSET]


# === END_CHUNK: BOOKING_VIEWS_V1 ===
