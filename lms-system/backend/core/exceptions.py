"""
Core exceptions for LMS System.

This module contains custom exception classes used across all apps.
"""

from rest_framework import status
from rest_framework.exceptions import APIException


class BadRequestException(APIException):
    """
    Exception for bad request errors.
    """
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Неверный запрос.'
    default_code = 'bad_request'


class UnauthorizedException(APIException):
    """
    Exception for unauthorized access.
    """
    
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Требуется авторизация.'
    default_code = 'unauthorized'


class ForbiddenException(APIException):
    """
    Exception for forbidden access.
    """
    
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Доступ запрещён.'
    default_code = 'forbidden'


class NotFoundException(APIException):
    """
    Exception for not found errors.
    """
    
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Объект не найден.'
    default_code = 'not_found'


class ConflictException(APIException):
    """
    Exception for conflict errors.
    """
    
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Конфликт данных.'
    default_code = 'conflict'


class ValidationException(APIException):
    """
    Exception for validation errors.
    """
    
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Ошибка валидации данных.'
    default_code = 'validation_error'


class RateLimitException(APIException):
    """
    Exception for rate limit exceeded.
    """
    
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Превышен лимит запросов.'
    default_code = 'rate_limit_exceeded'


class InternalServerException(APIException):
    """
    Exception for internal server errors.
    """
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Внутренняя ошибка сервера.'
    default_code = 'internal_server_error'


class ServiceUnavailableException(APIException):
    """
    Exception for service unavailable.
    """
    
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Сервис временно недоступен.'
    default_code = 'service_unavailable'