"""Quizzes app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class QuizzesConfig(AppConfig):
    """Configuration for Quizzes app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.quizzes'
    verbose_name = _('Тесты')