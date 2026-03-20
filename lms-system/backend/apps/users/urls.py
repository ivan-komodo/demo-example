"""
User URL configuration for LMS System.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    login_view,
    logout_view,
    password_reset_confirm_view,
    password_reset_request_view,
    register_view,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    
    # Password reset endpoints
    path('password/reset/', password_reset_request_view, name='password-reset'),
    path('password/reset/confirm/', password_reset_confirm_view, name='password-reset-confirm'),
]