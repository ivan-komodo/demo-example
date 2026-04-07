"""Notification views."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.utils import log_line
from .models import Notification
from .serializers import (
    MarkAsReadSerializer,
    NotificationCreateSerializer,
    NotificationSerializer,
)


# === CHUNK: NOTIFICATION_VIEWS_V1 [NOTIFICATIONS] ===
# Описание: ViewSet для управления уведомлениями пользователей.
# Dependencies: NOTIFICATION_MODELS_V1, NOTIFICATION_SERIALIZERS_V1, CORE_UTILS_V1


# [START_NOTIFICATION_VIEWSET]
"""
ANCHOR: NOTIFICATION_VIEWSET
PURPOSE: ViewSet для управления уведомлениями пользователей.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет CRUD операции для уведомлений
- предоставляет actions для отметки прочитанными

@Invariants:
- все действия требуют аутентификации
- пользователи видят только свои уведомления

@SideEffects:
- нет побочных эффектов на уровне класса

@ForbiddenChanges:
- permission_classes=[IsAuthenticated]
- пользователи не должны видеть чужие уведомления

@AllowedRefactorZone:
- можно добавлять новые actions
- можно расширять фильтрацию
"""
class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notification model."""
    
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    # [START_GET_NOTIFICATION_SERIALIZER_CLASS]
    """
    ANCHOR: GET_NOTIFICATION_SERIALIZER_CLASS
    PURPOSE: Выбор сериализатора в зависимости от действия.

    @PreConditions:
    - нет нетривиальных предусловий

    @PostConditions:
    - возвращает NotificationCreateSerializer для создания
    - возвращает NotificationSerializer для остальных действий

    @Invariants:
    - всегда возвращает класс сериализатора

    @SideEffects:
    - нет побочных эффектов

    @ForbiddenChanges:
    - NotificationCreateSerializer для action='create'
    """
    def get_serializer_class(self):
        log_line(
            "notifications",
            "DEBUG",
            "get_serializer_class",
            "GET_NOTIFICATION_SERIALIZER_CLASS",
            "ENTRY",
            {"action": self.action}
        )
        
        if self.action == 'create':
            log_line(
                "notifications",
                "DEBUG",
                "get_serializer_class",
                "GET_NOTIFICATION_SERIALIZER_CLASS",
                "BRANCH",
                {"branch": "create", "serializer": "NotificationCreateSerializer"}
            )
            result = NotificationCreateSerializer
        else:
            log_line(
                "notifications",
                "DEBUG",
                "get_serializer_class",
                "GET_NOTIFICATION_SERIALIZER_CLASS",
                "BRANCH",
                {"branch": "other", "serializer": "NotificationSerializer"}
            )
            result = NotificationSerializer
        
        log_line(
            "notifications",
            "DEBUG",
            "get_serializer_class",
            "GET_NOTIFICATION_SERIALIZER_CLASS",
            "EXIT",
            {"serializer": result.__name__}
        )
        return result
    # [END_GET_NOTIFICATION_SERIALIZER_CLASS]
    
    # [START_GET_NOTIFICATION_QUERYSET]
    """
    ANCHOR: GET_NOTIFICATION_QUERYSET
    PURPOSE: Фильтрация уведомлений по текущему пользователю.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - возвращает только уведомления текущего пользователя
    - результат отсортирован по created_at DESC

    @Invariants:
    - пользователи не могут видеть чужие уведомления

    @SideEffects:
    - нет побочных эффектов (только чтение)

    @ForbiddenChanges:
    - фильтрация по user=request.user (безопасность)
    """
    def get_queryset(self):
        log_line(
            "notifications",
            "DEBUG",
            "get_queryset",
            "GET_NOTIFICATION_QUERYSET",
            "ENTRY",
            {"user_id": self.request.user.id}
        )
        
        queryset = Notification.objects.filter(user=self.request.user)
        
        log_line(
            "notifications",
            "DEBUG",
            "get_queryset",
            "GET_NOTIFICATION_QUERYSET",
            "EXIT",
            {"user_id": self.request.user.id, "result": "queryset"}
        )
        return queryset
    # [END_GET_NOTIFICATION_QUERYSET]
    
    # [START_MARK_AS_READ_ACTION]
    """
    ANCHOR: MARK_AS_READ_ACTION
    PURPOSE: Пометить несколько уведомлений как прочитанные.

    @PreConditions:
    - request.user аутентифицирован
    - notification_ids содержит корректные ID

    @PostConditions:
    - помечает указанные уведомления как прочитанные
    - возвращает количество обновлённых записей
    - обновляет только уведомления текущего пользователя

    @Invariants:
    - могут быть обновлены только уведомления текущего пользователя
    - невалидные ID игнорируются

    @SideEffects:
    - обновление записей в БД

    @ForbiddenChanges:
    - фильтрация по user=request.user (безопасность)
    - валидация serializer.is_valid(raise_exception=True)
    """
    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        log_line(
            "notifications",
            "DEBUG",
            "mark_as_read",
            "MARK_AS_READ_ACTION",
            "ENTRY",
            {"user_id": request.user.id}
        )
        
        serializer = MarkAsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_ids = serializer.validated_data['notification_ids']
        log_line(
            "notifications",
            "DEBUG",
            "mark_as_read",
            "MARK_AS_READ_ACTION",
            "CHECK",
            {"check": "serializer_valid", "notification_ids": notification_ids}
        )
        
        updated = Notification.objects.filter(
            id__in=notification_ids,
            user=request.user
        ).update(is_read=True)
        
        log_line(
            "notifications",
            "INFO",
            "mark_as_read",
            "MARK_AS_READ_ACTION",
            "STATE_CHANGE",
            {"entity": "notification", "user_id": request.user.id, "updated": updated, "from": "unread", "to": "read"}
        )
        log_line(
            "notifications",
            "DEBUG",
            "mark_as_read",
            "MARK_AS_READ_ACTION",
            "EXIT",
            {"user_id": request.user.id, "updated": updated}
        )
        
        return Response({'updated': updated})
    # [END_MARK_AS_READ_ACTION]
    
    # [START_MARK_ALL_READ_ACTION]
    """
    ANCHOR: MARK_ALL_READ_ACTION
    PURPOSE: Пометить все уведомления пользователя как прочитанные.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - помечает все непрочитанные уведомления пользователя как прочитанные
    - возвращает количество обновлённых записей

    @Invariants:
    - обновляются только уведомления текущего пользователя
    - обновляются только is_read=False записи

    @SideEffects:
    - массовое обновление записей в БД

    @ForbiddenChanges:
    - фильтрация по user=request.user (безопасность)
    - фильтрация по is_read=False
    """
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        log_line(
            "notifications",
            "DEBUG",
            "mark_all_read",
            "MARK_ALL_READ_ACTION",
            "ENTRY",
            {"user_id": request.user.id}
        )
        
        updated = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        
        log_line(
            "notifications",
            "INFO",
            "mark_all_read",
            "MARK_ALL_READ_ACTION",
            "STATE_CHANGE",
            {"entity": "notification", "user_id": request.user.id, "updated": updated, "from": "unread", "to": "read"}
        )
        log_line(
            "notifications",
            "DEBUG",
            "mark_all_read",
            "MARK_ALL_READ_ACTION",
            "EXIT",
            {"user_id": request.user.id, "updated": updated}
        )
        
        return Response({'updated': updated})
    # [END_MARK_ALL_READ_ACTION]
    
    # [START_UNREAD_COUNT_ACTION]
    """
    ANCHOR: UNREAD_COUNT_ACTION
    PURPOSE: Получение количества непрочитанных уведомлений.

    @PreConditions:
    - request.user аутентифицирован

    @PostConditions:
    - возвращает количество непрочитанных уведомлений
    - возвращает только count для текущего пользователя

    @Invariants:
    - подсчёт только для текущего пользователя
    - подсчёт только is_read=False

    @SideEffects:
    - нет побочных эффектов (только чтение)

    @ForbiddenChanges:
    - фильтрация по user=request.user (безопасность)
    - фильтрация по is_read=False
    """
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        log_line(
            "notifications",
            "DEBUG",
            "unread_count",
            "UNREAD_COUNT_ACTION",
            "ENTRY",
            {"user_id": request.user.id}
        )
        
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        log_line(
            "notifications",
            "DEBUG",
            "unread_count",
            "UNREAD_COUNT_ACTION",
            "EXIT",
            {"user_id": request.user.id, "unread_count": count}
        )
        
        return Response({'unread_count': count})
    # [END_UNREAD_COUNT_ACTION]


# [END_NOTIFICATION_VIEWSET]


# === END_CHUNK: NOTIFICATION_VIEWS_V1 ===
