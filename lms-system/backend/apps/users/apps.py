"""Users app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    """Configuration for Users app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = _('Пользователи')
    
    def ready(self):
        """Import signal handlers when app is ready."""
        import apps.users.signals  # noqa: F401