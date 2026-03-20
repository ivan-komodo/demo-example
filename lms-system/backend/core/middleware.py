"""
Core middleware for LMS System.

This module contains middleware classes used across all apps.
"""

import logging
import time

from django.conf import settings
from django.http import HttpRequest

logger = logging.getLogger('lms')


class RequestLoggingMiddleware:
    """
    Middleware to log all requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest):
        # Log request
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Log response
        duration = time.time() - start_time
        log_data = {
            'method': request.method,
            'path': request.path,
            'status': response.status_code,
            'duration': f'{duration:.3f}s',
            'user': str(request.user) if request.user.is_authenticated else 'Anonymous',
            'ip': get_client_ip(request),
        }
        
        if response.status_code >= 400:
            logger.warning(f'Request: {log_data}')
        else:
            logger.info(f'Request: {log_data}')
        
        return response


class CORSMiddleware:
    """
    Custom CORS middleware for additional CORS handling.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest):
        response = self.get_response(request)
        
        # Add CORS headers if needed
        origin = request.META.get('HTTP_ORIGIN')
        if origin and origin in settings.CORS_ALLOWED_ORIGINS:
            response['Access-Control-Allow-Origin'] = origin
        
        return response


def get_client_ip(request: HttpRequest) -> str:
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')