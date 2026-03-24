"""Notification services."""

from django.conf import settings
from django.db import transaction

from .models import Notification


# === CHUNK: NOTIFICATION_SERVICES_V1 [NOTIFICATIONS] ===
# Описание: Бизнес-логика для работы с уведомлениями.
# Dependencies: NOTIFICATION_MODELS_V1


# [START_NOTIFICATION_SERVICE_CLASS]
# ANCHOR: NOTIFICATION_SERVICE_CLASS
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет методы для создания и управления уведомлениями
# PURPOSE: Сервисный класс для инкапсуляции бизнес-логики уведомлений.
class NotificationService:
    """Service class for notification operations."""
    
    # [START_CREATE_NOTIFICATION]
    # ANCHOR: CREATE_NOTIFICATION
    # @PreConditions:
    # - user_id существует в БД
    # - type валидный тип уведомления
    # - title и message непустые строки
    # @PostConditions:
    # - создаёт и возвращает экземпляр Notification
    # PURPOSE: Создание одного уведомления для пользователя.
    @staticmethod
    def create_notification(user_id: int, type: str, title: str, message: str) -> Notification:
        """Create a notification for a user."""
        return Notification.objects.create(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
        )
    # [END_CREATE_NOTIFICATION]
    
    # [START_CREATE_BULK_NOTIFICATIONS]
    # ANCHOR: CREATE_BULK_NOTIFICATIONS
    # @PreConditions:
    # - user_ids список существующих ID пользователей
    # - type валидный тип уведомления
    # - title и message непустые строки
    # @PostConditions:
    # - создаёт уведомления для всех указанных пользователей
    # - возвращает количество созданных уведомлений
    # PURPOSE: Массовое создание уведомлений для нескольких пользователей.
    @staticmethod
    def create_bulk_notifications(
        user_ids: list[int],
        type: str,
        title: str,
        message: str,
    ) -> int:
        """Create notifications for multiple users."""
        notifications = [
            Notification(
                user_id=user_id,
                type=type,
                title=title,
                message=message,
            )
            for user_id in user_ids
        ]
        created = Notification.objects.bulk_create(notifications)
        return len(created)
    # [END_CREATE_BULK_NOTIFICATIONS]
    
    # [START_GET_UNREAD_NOTIFICATIONS]
    # ANCHOR: GET_UNREAD_NOTIFICATIONS
    # @PreConditions:
    # - user_id существует в БД
    # @PostConditions:
    # - возвращает QuerySet непрочитанных уведомлений пользователя
    # PURPOSE: Получение списка непрочитанных уведомлений пользователя.
    @staticmethod
    def get_unread_notifications(user_id: int):
        """Get unread notifications for a user."""
        return Notification.objects.filter(
            user_id=user_id,
            is_read=False,
        ).order_by('-created_at')
    # [END_GET_UNREAD_NOTIFICATIONS]
    
    # [START_MARK_ALL_READ]
    # ANCHOR: MARK_ALL_READ
    # @PreConditions:
    # - user_id существует в БД
    # @PostConditions:
    # - помечает все непрочитанные уведомления пользователя как прочитанные
    # - возвращает количество обновлённых записей
    # PURPOSE: Пометить все уведомления пользователя как прочитанные.
    @staticmethod
    def mark_all_read(user_id: int) -> int:
        """Mark all notifications as read for a user."""
        return Notification.objects.filter(
            user_id=user_id,
            is_read=False,
        ).update(is_read=True)
    # [END_MARK_ALL_READ]


# [END_NOTIFICATION_SERVICE_CLASS]


# === END_CHUNK: NOTIFICATION_SERVICES_V1 ===