"""Progress app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProgressConfig(AppConfig):
    """Configuration for Progress app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.progress'
    verbose_name = _('Прогресс')