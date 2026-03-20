"""Courses app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoursesConfig(AppConfig):
    """Configuration for Courses app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.courses'
    verbose_name = _('Курсы')
    
    def ready(self):
        """Import signal handlers when app is ready."""
        import apps.courses.signals  # noqa: F401