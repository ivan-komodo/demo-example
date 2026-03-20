"""Courses admin configuration."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Course, CourseEnrollment, Module


class ModuleInline(admin.TabularInline):
    """Inline admin for Module."""
    
    model = Module
    extra = 1
    fields = ['title', 'content_type', 'order_num']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for Course model."""
    
    list_display = ['title', 'status', 'modules_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ModuleInline]
    
    def modules_count(self, obj):
        return obj.modules.count()
    modules_count.short_description = _('Количество модулей')


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    """Admin configuration for Module model."""
    
    list_display = ['title', 'course', 'content_type', 'order_num', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['title', 'course__title']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['course']


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for CourseEnrollment model."""
    
    list_display = ['user', 'course', 'status', 'enrolled_at', 'completed_at']
    list_filter = ['status', 'enrolled_at']
    search_fields = ['user__email', 'course__title']
    readonly_fields = ['enrolled_at', 'completed_at']
    raw_id_fields = ['user', 'course']