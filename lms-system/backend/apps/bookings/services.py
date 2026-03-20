"""Booking services."""

from django.contrib.auth import get_user_model

from .models import Booking, Resource

User = get_user_model()


class BookingService:
    """Service for booking management."""
    
    @staticmethod
    def check_availability(resource: Resource, start_time, end_time, exclude_booking=None) -> bool:
        """Check if resource is available for booking."""
        queryset = Booking.objects.filter(
            resource=resource,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        )
        
        if exclude_booking:
            queryset = queryset.exclude(pk=exclude_booking.pk)
        
        return not queryset.exists()
    
    @staticmethod
    def get_user_bookings(user: User):
        """Get all bookings for a user."""
        return Booking.objects.filter(user=user).select_related('resource', 'course')
    
    @staticmethod
    def get_resource_bookings(resource: Resource):
        """Get all bookings for a resource."""
        return Booking.objects.filter(resource=resource).select_related('user', 'course')