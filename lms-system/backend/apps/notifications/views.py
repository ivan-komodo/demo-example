"""Notification views."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import (
    MarkAsReadSerializer,
    NotificationCreateSerializer,
    NotificationSerializer,
)


# === CHUNK: NOTIFICATION_VIEWS_V1 [NOTIFICATIONS] ===
# Описание: ViewSet для управления уведомлениями пользователей.
# Dependencies: NOTIFICATION_MODELS_V1, NOTIFICATION_SERIALIZERS_V1


# [START_NOTIFICATION_VIEWSET]
# ANCHOR: NOTIFICATION_VIEWSET
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет CRUD операции для уведомлений
# - предоставляет actions для отметки прочитанными
# PURPOSE: ViewSet для управления уведомлениями пользователей.
class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notification model."""
    
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    # [START_GET_NOTIFICATION_SERIALIZER_CLASS]
    # ANCHOR: GET_NOTIFICATION_SERIALIZER_CLASS
    # @PreConditions:
    # - нет нетривиальных предусловий
    # @PostConditions:
    # - возвращает NotificationCreateSerializer для создания, иначе NotificationSerializer
    # PURPOSE: Выбор сериализатора в зависимости от действия.
    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    # [END_GET_NOTIFICATION_SERIALIZER_CLASS]
    
    # [START_GET_NOTIFICATION_QUERYSET]
    # ANCHOR: GET_NOTIFICATION_QUERYSET
    # @PreConditions:
    # - request.user аутентифицирован
    # @PostConditions:
    # - возвращает только уведомления текущего пользователя
    # PURPOSE: Фильтрация уведомлений по текущему пользователю.
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    # [END_GET_NOTIFICATION_QUERYSET]
    
    # [START_MARK_AS_READ_ACTION]
    # ANCHOR: MARK_AS_READ_ACTION
    # @PreConditions:
    # - request.user аутентифицирован
    # - notification_ids содержит корректные ID
    # @PostConditions:
    # - помечает указанные уведомления как прочитанные
    # PURPOSE: Пометить несколько уведомлений как прочитанные.
    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        """Mark multiple notifications as read."""
        serializer = MarkAsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_ids = serializer.validated_data['notification_ids']
        updated = Notification.objects.filter(
            id__in=notification_ids,
            user=request.user
        ).update(is_read=True)
        
        return Response({'updated': updated})
    # [END_MARK_AS_READ_ACTION]
    
    # [START_MARK_ALL_READ_ACTION]
    # ANCHOR: MARK_ALL_READ_ACTION
    # @PreConditions:
    # - request.user аутентифицирован
    # @PostConditions:
    # - помечает все непрочитанные уведомления пользователя как прочитанные
    # PURPOSE: Пометить все уведомления пользователя как прочитанные.
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        updated = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response({'updated': updated})
    # [END_MARK_ALL_READ_ACTION]
    
    # [START_UNREAD_COUNT_ACTION]
    # ANCHOR: UNREAD_COUNT_ACTION
    # @PreConditions:
    # - request.user аутентифицирован
    # @PostConditions:
    # - возвращает количество непрочитанных уведомлений
    # PURPOSE: Получение количества непрочитанных уведомлений.
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return Response({'unread_count': count})
    # [END_UNREAD_COUNT_ACTION]


# [END_NOTIFICATION_VIEWSET]


# === END_CHUNK: NOTIFICATION_VIEWS_V1 ===