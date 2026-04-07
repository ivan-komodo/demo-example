"""Booking services."""

from django.contrib.auth import get_user_model

from core.utils import log_line

from .models import Booking, Resource

User = get_user_model()


# === CHUNK: BOOKING_SERVICES_V1 [BOOKINGS] ===
# Описание: Бизнес-логика для управления бронированиями.
# Dependencies: BOOKING_MODELS_V1


# [START_BOOKING_SERVICE_CLASS]
"""
ANCHOR: BOOKING_SERVICE_CLASS
PURPOSE: Сервисный класс для инкапсуляции бизнес-логики бронирований.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет статические методы для проверки доступности и получения бронирований
- не хранит состояние

@Invariants:
- все методы статические
- не изменяет состояние базы данных напрямую (только чтение)

@SideEffects:
- нет побочных эффектов на уровне класса

@ForbiddenChanges:
- статическая природа методов (не превращать в instance methods)
"""
class BookingService:
    """Service for booking management."""
    
    # [START_CHECK_AVAILABILITY]
    """
    ANCHOR: CHECK_AVAILABILITY
    PURPOSE: Проверка доступности ресурса для бронирования на указанный период.

    @PreConditions:
    - resource существует (не None)
    - start_time задан и валиден
    - end_time задан и валиден, start_time < end_time
    - exclude_booking опционален (может быть None)

    @PostConditions:
    - возвращает True если ресурс доступен (нет конфликтов)
    - возвращает False если есть конфликт с existing booking
    - исключает exclude_booking из проверки если задан

    @Invariants:
    - не изменяет состояние БД
    - проверяет только PENDING и CONFIRMED статусы

    @SideEffects:
    - нет побочных эффектов (только чтение БД)

    @ForbiddenChanges:
    - логика пересечения интервалов
    - проверяемые статусы (PENDING, CONFIRMED)
    """
    @staticmethod
    def check_availability(resource: Resource, start_time, end_time, exclude_booking=None) -> bool:
        """Check if resource is available for booking."""
        log_line("bookings", "DEBUG", "check_availability", "CHECK_AVAILABILITY", "ENTRY", {
            "resource_id": resource.pk,
            "start_time": str(start_time),
            "end_time": str(end_time),
            "exclude_booking_id": exclude_booking.pk if exclude_booking else None,
        })
        
        queryset = Booking.objects.filter(
            resource=resource,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        )
        
        if exclude_booking:
            log_line("bookings", "DEBUG", "check_availability", "CHECK_AVAILABILITY", "BRANCH", {
                "branch": "exclude_booking",
                "exclude_booking_id": exclude_booking.pk,
            })
            queryset = queryset.exclude(pk=exclude_booking.pk)
        
        has_conflict = queryset.exists()
        is_available = not has_conflict
        
        log_line("bookings", "DEBUG", "check_availability", "CHECK_AVAILABILITY", "CHECK", {
            "check": "availability",
            "result": is_available,
            "has_conflict": has_conflict,
        })
        
        log_line("bookings", "DEBUG", "check_availability", "CHECK_AVAILABILITY", "EXIT", {
            "result": "available" if is_available else "unavailable",
            "resource_id": resource.pk,
        })
        return is_available
    # [END_CHECK_AVAILABILITY]
    
    # [START_GET_USER_BOOKINGS]
    """
    ANCHOR: GET_USER_BOOKINGS
    PURPOSE: Получение всех бронирований указанного пользователя.

    @PreConditions:
    - user аутентифицирован (не None)

    @PostConditions:
    - возвращает QuerySet с бронированиями пользователя
    - бронирования включают связанные resource и course (select_related)

    @Invariants:
    - возвращает QuerySet (не список)
    - не фильтрует по статусу (возвращает все)

    @SideEffects:
    - нет побочных эффектов (только чтение БД)

    @ForbiddenChanges:
    - select_related для resource и course (оптимизация)
    """
    @staticmethod
    def get_user_bookings(user: User):
        """Get all bookings for a user."""
        log_line("bookings", "DEBUG", "get_user_bookings", "GET_USER_BOOKINGS", "ENTRY", {
            "user_id": user.pk,
        })
        
        result = Booking.objects.filter(user=user).select_related('resource', 'course')
        
        log_line("bookings", "DEBUG", "get_user_bookings", "GET_USER_BOOKINGS", "EXIT", {
            "result": "queryset",
            "user_id": user.pk,
        })
        return result
    # [END_GET_USER_BOOKINGS]
    
    # [START_GET_RESOURCE_BOOKINGS]
    """
    ANCHOR: GET_RESOURCE_BOOKINGS
    PURPOSE: Получение всех бронирований указанного ресурса.

    @PreConditions:
    - resource существует (не None)

    @PostConditions:
    - возвращает QuerySet с бронированиями ресурса
    - бронирования включают связанные user и course (select_related)

    @Invariants:
    - возвращает QuerySet (не список)
    - не фильтрует по статусу (возвращает все)

    @SideEffects:
    - нет побочных эффектов (только чтение БД)

    @ForbiddenChanges:
    - select_related для user и course (оптимизация)
    """
    @staticmethod
    def get_resource_bookings(resource: Resource):
        """Get all bookings for a resource."""
        log_line("bookings", "DEBUG", "get_resource_bookings", "GET_RESOURCE_BOOKINGS", "ENTRY", {
            "resource_id": resource.pk,
        })
        
        result = Booking.objects.filter(resource=resource).select_related('user', 'course')
        
        log_line("bookings", "DEBUG", "get_resource_bookings", "GET_RESOURCE_BOOKINGS", "EXIT", {
            "result": "queryset",
            "resource_id": resource.pk,
        })
        return result
    # [END_GET_RESOURCE_BOOKINGS]


# [END_BOOKING_SERVICE_CLASS]


# === END_CHUNK: BOOKING_SERVICES_V1 ===
