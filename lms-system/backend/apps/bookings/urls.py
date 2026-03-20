"""Booking URLs."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, ResourceViewSet

router = DefaultRouter()
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
]