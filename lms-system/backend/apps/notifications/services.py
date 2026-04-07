"""Notification services."""

from django.conf import settings
from django.db import transaction

from core.utils import log_line
from .models import Notification


# === CHUNK: NOTIFICATION_SERVICES_V1 [NOTIFICATIONS] ===
# Описание: Бизнес-логика для работы с уведомлениями.
# Dependencies: NOTIFICATION_MODELS_V1, CORE_UTILS_V1


# [START_NOTIFICATION_SERVICE_CLASS]
"""
ANCHOR: NOTIFICATION_SERVICE_CLASS
PURPOSE: Сервисный класс для инкапсуляции бизнес-логики уведомлений.

@PreConditions:
- нет нетривиальных предусловий для класса

@PostConditions:
- предоставляет методы для создания и управления уведомлениями

@Invariants:
- все методы статические (не требуют экземпляра)

@SideEffects:
- нет побочных эффектов на уровне класса

@ForbiddenChanges:
- все методы должны оставаться статическими

@AllowedRefactorZone:
- можно добавлять новые методы
- можно оптимизировать запросы к БД
"""
class NotificationService:
    """Service class for notification operations."""
    
    # [START_CREATE_NOTIFICATION]
    """
    ANCHOR: CREATE_NOTIFICATION
    PURPOSE: Создание одного уведомления для пользователя.

    @PreConditions:
    - user_id существует в БД
    - type валидный тип уведомления (info/warning/success/error)
    - title и message непустые строки

    @PostConditions:
    - создаёт и возвращает экземпляр Notification
    - уведомление сохранено в БД

    @Invariants:
    - is_read всегда False при создании
    - created_at устанавливается автоматически

    @SideEffects:
    - создание записи в БД

    @ForbiddenChanges:
    - is_read=False по умолчанию при создании
    """
    @staticmethod
    def create_notification(user_id: int, type: str, title: str, message: str) -> Notification:
        log_line(
            "notifications",
            "DEBUG",
            "create_notification",
            "CREATE_NOTIFICATION",
            "ENTRY",
            {"user_id": user_id, "type": type, "title": title[:50]}
        )
        
        notification = Notification.objects.create(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
        )
        
        log_line(
            "notifications",
            "INFO",
            "create_notification",
            "CREATE_NOTIFICATION",
            "STATE_CHANGE",
            {"entity": "notification", "id": notification.id, "user_id": user_id, "type": type}
        )
        log_line(
            "notifications",
            "DEBUG",
            "create_notification",
            "CREATE_NOTIFICATION",
            "EXIT",
            {"result": "success", "notification_id": notification.id}
        )
        return notification
    # [END_CREATE_NOTIFICATION]
    
    # [START_CREATE_BULK_NOTIFICATIONS]
    """
    ANCHOR: CREATE_BULK_NOTIFICATIONS
    PURPOSE: Массовое создание уведомлений для нескольких пользователей.

    @PreConditions:
    - user_ids список существующих ID пользователей
    - type валидный тип уведомления
    - title и message непустые строки

    @PostConditions:
    - создаёт уведомления для всех указанных пользователей
    - возвращает количество созданных уведомлений

    @Invariants:
    - все уведомления создаются с одинаковыми title/message/type
    - is_read=False для всех

    @SideEffects:
    - массовая вставка записей в БД (bulk_create)

    @ForbiddenChanges:
    - использование bulk_create для оптимизации
    - одинаковые данные для всех пользователей
    """
    @staticmethod
    def create_bulk_notifications(
        user_ids: list[int],
        type: str,
        title: str,
        message: str,
    ) -> int:
        log_line(
            "notifications",
            "DEBUG",
            "create_bulk_notifications",
            "CREATE_BULK_NOTIFICATIONS",
            "ENTRY",
            {"user_count": len(user_ids), "type": type, "title": title[:50]}
        )
        
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
        count = len(created)
        
        log_line(
            "notifications",
            "INFO",
            "create_bulk_notifications",
            "CREATE_BULK_NOTIFICATIONS",
            "STATE_CHANGE",
            {"entity": "notification", "count": count, "type": type}
        )
        log_line(
            "notifications",
            "DEBUG",
            "create_bulk_notifications",
            "CREATE_BULK_NOTIFICATIONS",
            "EXIT",
            {"result": "success", "count": count}
        )
        return count
    # [END_CREATE_BULK_NOTIFICATIONS]
    
    # [START_GET_UNREAD_NOTIFICATIONS]
    """
    ANCHOR: GET_UNREAD_NOTIFICATIONS
    PURPOSE: Получение списка непрочитанных уведомлений пользователя.

    @PreConditions:
    - user_id существует в БД

    @PostConditions:
    - возвращает QuerySet непрочитанных уведомлений пользователя
    - результат отсортирован по created_at DESC

    @Invariants:
    - возвращает только уведомления указанного пользователя
    - возвращает только is_read=False

    @SideEffects:
    - нет побочных эффектов (только чтение)

    @ForbiddenChanges:
    - фильтрация по is_read=False
    - сортировка по created_at DESC
    """
    @staticmethod
    def get_unread_notifications(user_id: int):
        log_line(
            "notifications",
            "DEBUG",
            "get_unread_notifications",
            "GET_UNREAD_NOTIFICATIONS",
            "ENTRY",
            {"user_id": user_id}
        )
        
        queryset = Notification.objects.filter(
            user_id=user_id,
            is_read=False,
        ).order_by('-created_at')
        
        log_line(
            "notifications",
            "DEBUG",
            "get_unread_notifications",
            "GET_UNREAD_NOTIFICATIONS",
            "EXIT",
            {"user_id": user_id, "result": "queryset"}
        )
        return queryset
    # [END_GET_UNREAD_NOTIFICATIONS]
    
    # [START_MARK_ALL_READ]
    """
    ANCHOR: MARK_ALL_READ
    PURPOSE: Пометить все уведомления пользователя как прочитанные.

    @PreConditions:
    - user_id существует в БД

    @PostConditions:
    - помечает все непрочитанные уведомления пользователя как прочитанные
    - возвращает количество обновлённых записей

    @Invariants:
    - обновляются только уведомления указанного пользователя
    - обновляются только is_read=False записи

    @SideEffects:
    - массовое обновление записей в БД

    @ForbiddenChanges:
    - обновление только is_read=True (не затрагивает другие поля)
    - фильтрация по user_id и is_read=False
    """
    @staticmethod
    def mark_all_read(user_id: int) -> int:
        log_line(
            "notifications",
            "DEBUG",
            "mark_all_read",
            "MARK_ALL_READ",
            "ENTRY",
            {"user_id": user_id}
        )
        
        count = Notification.objects.filter(
            user_id=user_id,
            is_read=False,
        ).update(is_read=True)
        
        log_line(
            "notifications",
            "INFO",
            "mark_all_read",
            "MARK_ALL_READ",
            "STATE_CHANGE",
            {"entity": "notification", "user_id": user_id, "count": count, "from": "unread", "to": "read"}
        )
        log_line(
            "notifications",
            "DEBUG",
            "mark_all_read",
            "MARK_ALL_READ",
            "EXIT",
            {"user_id": user_id, "count": count}
        )
        return count
    # [END_MARK_ALL_READ]


# [END_NOTIFICATION_SERVICE_CLASS]


# === END_CHUNK: NOTIFICATION_SERVICES_V1 ===
