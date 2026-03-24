"""
Core middleware for LMS System.

This module contains middleware classes used across all apps.
"""

import logging
import time

from django.conf import settings
from django.http import HttpRequest

logger = logging.getLogger('lms')


# === CHUNK: CORE_MIDDLEWARE_V1 [CORE] ===
# Описание: Middleware для логирования запросов и CORS.
# Dependencies: none


# [START_REQUEST_LOGGING_MIDDLEWARE]
# ANCHOR: REQUEST_LOGGING_MIDDLEWARE
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - логирует все HTTP запросы с метаданными
# PURPOSE: Middleware для логирования всех входящих запросов.
class RequestLoggingMiddleware:
    """
    Middleware to log all requests.
    """
    
    # [START_REQUEST_LOGGING_INIT]
    # ANCHOR: REQUEST_LOGGING_INIT
    # @PreConditions:
    # - get_response вызываемый объект
    # @PostConditions:
    # - сохраняет get_response для последующего использования
    # PURPOSE: Инициализация middleware с функцией get_response.
    def __init__(self, get_response):
        self.get_response = get_response
    # [END_REQUEST_LOGGING_INIT]
    
    # [START_REQUEST_LOGGING_CALL]
    # ANCHOR: REQUEST_LOGGING_CALL
    # @PreConditions:
    # - request валидный HttpRequest объект
    # @PostConditions:
    # - логирует запрос с методом, путём, статусом, длительностью, пользователем, IP
    # - возвращает response
    # PURPOSE: Обработка запроса и логирование с метриками.
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
    # [END_REQUEST_LOGGING_CALL]


# [END_REQUEST_LOGGING_MIDDLEWARE]


# [START_CORS_MIDDLEWARE]
# ANCHOR: CORS_MIDDLEWARE
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - добавляет CORS заголовки для разрешённых origins
# PURPOSE: Кастомная CORS middleware для обработки кросс-доменных запросов.
class CORSMiddleware:
    """
    Custom CORS middleware for additional CORS handling.
    """
    
    # [START_CORS_INIT]
    # ANCHOR: CORS_INIT
    # @PreConditions:
    # - get_response вызываемый объект
    # @PostConditions:
    # - сохраняет get_response для последующего использования
    # PURPOSE: Инициализация CORS middleware.
    def __init__(self, get_response):
        self.get_response = get_response
    # [END_CORS_INIT]
    
    # [START_CORS_CALL]
    # ANCHOR: CORS_CALL
    # @PreConditions:
    # - request валидный HttpRequest объект
    # @PostConditions:
    # - добавляет Access-Control-Allow-Origin для разрешённых origins
    # - возвращает response
    # PURPOSE: Обработка CORS заголовков в ответе.
    def __call__(self, request: HttpRequest):
        response = self.get_response(request)
        
        # Add CORS headers if needed
        origin = request.META.get('HTTP_ORIGIN')
        if origin and origin in settings.CORS_ALLOWED_ORIGINS:
            response['Access-Control-Allow-Origin'] = origin
        
        return response
    # [END_CORS_CALL]


# [END_CORS_MIDDLEWARE]


# [START_GET_CLIENT_IP]
# ANCHOR: GET_CLIENT_IP
# @PreConditions:
# - request валидный HttpRequest объект
# @PostConditions:
# - возвращает IP адрес клиента (из X-Forwarded-For или REMOTE_ADDR)
# PURPOSE: Получение IP адреса клиента из запроса.
def get_client_ip(request: HttpRequest) -> str:
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')
# [END_GET_CLIENT_IP]


# === END_CHUNK: CORE_MIDDLEWARE_V1 ===