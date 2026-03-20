"""Progress services."""

from django.contrib.auth import get_user_model

from apps.courses.models import Module

from .models import UserProgress

User = get_user_model()


class ProgressService:
    """Service for progress management."""
    
    @staticmethod
    def get_or_create_progress(user: User, module: Module) -> UserProgress:
        """Get or create progress for a user and module."""
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            module=module,
            defaults={'status': UserProgress.Status.NOT_STARTED}
        )
        return progress
    
    @staticmethod
    def mark_in_progress(user: User, module: Module) -> UserProgress:
        """Mark module as in progress."""
        progress = ProgressService.get_or_create_progress(user, module)
        progress.mark_in_progress()
        return progress
    
    @staticmethod
    def mark_completed(user: User, module: Module, score=None) -> UserProgress:
        """Mark module as completed."""
        progress = ProgressService.get_or_create_progress(user, module)
        progress.mark_completed(score)
        return progress