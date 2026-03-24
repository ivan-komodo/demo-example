"""
Core exceptions for LMS System.

This module contains custom exception classes used across all apps.
"""

from rest_framework import status
from rest_framework.exceptions import APIException


# === CHUNK: CORE_EXCEPTIONS_V1 [CORE] ===
# Описание: Кастомные исключения для API.
# Dependencies: none


# [START_BAD_REQUEST_EXCEPTION]
# ANCHOR: BAD_REQUEST_EXCEPTION
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - возвращает HTTP 400 с деталями ошибки
# PURPOSE: Исключение для ошибок некорректного запроса.
class BadRequestException(APIException):
    """
    Exception for bad request errors.
    """
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Неверный запрос.'
    default_code = 'bad_request'
# [END_BAD_REQUEST_EXCEPTION]


# [START_UNAUTHORIZED_EXCEPTION]
# ANCHOR: UNAUTHORIZED_EXCEPTION
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - возвращает HTTP 401 с деталями ошибки
# PURPOSE: Исключение для неавторизованного доступа.
class UnauthorizedException(APIException):
    """
    Exception for unauthorized access.
    """
    
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Требуется авторизация.'
    default_code = 'unauthorized'
# [END_UNAUTHORIZED_EXCEPTION]


# [START_FORBIDDEN_EXCEPTION]
# ANCHOR: FORBIDDEN_EXCEPTION
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - возвращает HTTP 403 с деталями ошибки
# PURPOSE: Исключение для запрещённого доступа.
class ForbiddenException(APIException):
    """
    Exception for forbidden access.
    """
    
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Доступ запрещён.'
    default_code = 'forbidden'
# [END_FORBIDDEN_EXCEPTION]


# [START_NOT_FOUND_EXCEPTION]
# ANCHOR: NOT_FOUND_EXCEPTION
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - возвращает HTTP 404 с деталями ошибки
# PURPOSE: Исключение для ненайденного объекта.
class NotFoundException(APIException):
    """
    Exception for not found errors.
    """
    
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Объект не найден.'
    default_code = 'not_found'
# [END_NOT_FOUND_EXCEPTION]


# [START_CONFLICT_EXCEPTION]
# ANCHOR: CONFLICT_EXCEPTION
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - возвращает HTTP 409 с деталями ошибки
# PURPOSE: Исключение для конфликтов данных.
class ConflictException(APIException):
    """
    Exception for conflict errors.
    """
    
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Конфликт данных.'
    default_code = 'conflict'
# [END_CONFLICT_EXCEPTION]


# [START_VALIDATION_EXCEPTION]
# ANCHOR: VALIDATION_EXCEPTION
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - возвращает HTTP 422 с деталями ошибки
# PURPOSE: Исключение для ошибок валидации.
class ValidationException(APIException):
    """
    Exception for validation errors.
    """
    
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Ошибка валидации данных.'
    default_code = 'validation_error'
# [END_VALIDATION_EXCEPTION]


# [START_RATE_LIMIT_EXCEPTION]
# ANCHOR: RATE_LIMIT_EXCEPTION
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - возвращает HTTP 429 с деталями ошибки
# PURPOSE: Исключение для превышения лимита запросов.
class RateLimitException(APIException):
    """
    Exception for rate limit exceeded.
    """
    
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Превышен лимит запросов.'
    default_code = 'rate_limit_exceeded'
# [END_RATE_LIMIT_EXCEPTION]


# [START_INTERNAL_SERVER_EXCEPTION]
# ANCHOR: INTERNAL_SERVER_EXCEPTION
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - возвращает HTTP 500 с деталями ошибки
# PURPOSE: Исключение для внутренних ошибок сервера.
class InternalServerException(APIException):
    """
    Exception for internal server errors.
    """
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Внутренняя ошибка сервера.'
    default_code = 'internal_server_error'
# [END_INTERNAL_SERVER_EXCEPTION]


# [START_SERVICE_UNAVAILABLE_EXCEPTION]
# ANCHOR: SERVICE_UNAVAILABLE_EXCEPTION
# @PreConditions:
# - нет нетривиальных предусловий
# @PostConditions:
# - возвращает HTTP 503 с деталями ошибки
# PURPOSE: Исключение для недоступности сервиса.
class ServiceUnavailableException(APIException):
    """
    Exception for service unavailable.
    """
    
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Сервис временно недоступен.'
    default_code = 'service_unavailable'
# [END_SERVICE_UNAVAILABLE_EXCEPTION]


# === END_CHUNK: CORE_EXCEPTIONS_V1 ===