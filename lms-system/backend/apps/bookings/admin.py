"""Bookings admin."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Booking, Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'capacity', 'is_active', 'created_at']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource', 'user', 'start_time', 'end_time', 'status']
    list_filter = ['status', 'start_time']
    search_fields = ['title', 'resource__name', 'user__email']
    raw_id_fields = ['resource', 'user', 'course']