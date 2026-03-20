"""Progress admin."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import UserProgress


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'status', 'completed_at', 'score']
    list_filter = ['status', 'completed_at']
    search_fields = ['user__email', 'module__title']
    raw_id_fields = ['user', 'module']