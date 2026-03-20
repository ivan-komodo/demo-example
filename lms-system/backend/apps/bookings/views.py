"""Booking views."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsAdminUser

from .models import Booking, Resource
from .serializers import BookingCreateSerializer, BookingSerializer, ResourceSerializer


class ResourceViewSet(viewsets.ModelViewSet):
    """ViewSet for Resource model."""
    
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for Booking model."""
    
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer
    
    def get_queryset(self):
        queryset = Booking.objects.select_related('resource', 'user', 'course')
        
        if not self.request.user.is_admin:
            queryset = queryset.filter(user=self.request.user)
        
        resource_id = self.request.query_params.get('resource_id')
        if resource_id:
            queryset = queryset.filter(resource_id=resource_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        booking = self.get_object()
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=['status'])
        return Response({'message': 'Бронирование отменено.'})