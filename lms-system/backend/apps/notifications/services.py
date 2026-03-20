"""Notification services."""

from django.contrib.auth import get_user_model

from .models import Notification

User = get_user_model()


class NotificationService:
    """Service for notification management."""
    
    @staticmethod
    def create_notification(
        user: User,
        title: str,
        message: str,
        notification_type: str = Notification.Type.INFO
    ) -> Notification:
        """
        Create a notification for a user.
        
        Args:
            user: User instance
            title: Notification title
            message: Notification message
            notification_type: Type of notification (info, warning, success, error)
            
        Returns:
            Created Notification instance
        """
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            type=notification_type
        )
    
    @staticmethod
    def create_bulk_notifications(
        users: list,
        title: str,
        message: str,
        notification_type: str = Notification.Type.INFO
    ) -> list:
        """
        Create notifications for multiple users.
        
        Args:
            users: List of User instances
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            
        Returns:
            List of created Notification instances
        """
        notifications = []
        for user in users:
            notifications.append(
                Notification(
                    user=user,
                    title=title,
                    message=message,
                    type=notification_type
                )
            )
        return Notification.objects.bulk_create(notifications)
    
    @staticmethod
    def get_unread_notifications(user: User):
        """Get unread notifications for a user."""
        return Notification.objects.filter(user=user, is_read=False)
    
    @staticmethod
    def mark_all_read(user: User) -> int:
        """Mark all notifications as read for a user."""
        return Notification.objects.filter(
            user=user,
            is_read=False
        ).update(is_read=True)