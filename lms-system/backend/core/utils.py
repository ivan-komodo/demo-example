"""
Core utilities for LMS System.

This module contains utility functions used across all apps.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger('lms')


# === CHUNK: CORE_UTILS_V1 [CORE] ===
# Описание: Утилиты общего назначения для всего проекта.
# Dependencies: none


# [START_SEND_EMAIL]
# ANCHOR: SEND_EMAIL
# @PreConditions:
# - subject, message непустые строки
# - recipient_list непустой список email адресов
# @PostConditions:
# - возвращает True при успешной отправке, False при ошибке
# PURPOSE: Отправка email сообщения через Django mail backend.
def send_email(
    subject: str,
    message: str,
    recipient_list: List[str],
    html_message: Optional[str] = None,
    from_email: Optional[str] = None,
) -> bool:
    """
    Send an email.
    
    Args:
        subject: Email subject
        message: Email message (plain text)
        recipient_list: List of recipient email addresses
        html_message: Optional HTML message
        from_email: Optional sender email
        
    Returns:
        True if email was sent successfully, False otherwise
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f'Failed to send email: {e}')
        return False
# [END_SEND_EMAIL]


# [START_SEND_TEMPLATE_EMAIL]
# ANCHOR: SEND_TEMPLATE_EMAIL
# @PreConditions:
# - subject непустая строка
# - template_name путь к существующему шаблону
# - context словарь с данными для шаблона
# - recipient_list непустой список email адресов
# @PostConditions:
# - возвращает True при успешной отправке, False при ошибке
# PURPOSE: Отправка email по HTML шаблону с текстовой версией.
def send_template_email(
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    recipient_list: List[str],
    from_email: Optional[str] = None,
) -> bool:
    """
    Send an email using a template.
    
    Args:
        subject: Email subject
        template_name: Name of the template file
        context: Context for template rendering
        recipient_list: List of recipient email addresses
        from_email: Optional sender email
        
    Returns:
        True if email was sent successfully, False otherwise
    """
    try:
        html_message = render_to_string(template_name, context)
        plain_message = render_to_string(template_name.replace('.html', '.txt'), context)
        
        return send_email(
            subject=subject,
            message=plain_message,
            recipient_list=recipient_list,
            html_message=html_message,
            from_email=from_email,
        )
    except Exception as e:
        logger.error(f'Failed to send template email: {e}')
        return False
# [END_SEND_TEMPLATE_EMAIL]


# [START_FORMAT_CURRENCY]
# ANCHOR: FORMAT_CURRENCY
# @PreConditions:
# - amount валидное Decimal значение
# - currency код валюты (по умолчанию RUB)
# @PostConditions:
# - возвращает строку формата "1,234.56 RUB"
# PURPOSE: Форматирование суммы как валюты.
def format_currency(amount: Decimal, currency: str = 'RUB') -> str:
    """
    Format amount as currency.
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    return f'{amount:,.2f} {currency}'
# [END_FORMAT_CURRENCY]


# [START_CALCULATE_PERCENTAGE]
# ANCHOR: CALCULATE_PERCENTAGE
# @PreConditions:
# - value, total валидные Decimal значения
# @PostConditions:
# - возвращает процент value от total (0 при total=0)
# PURPOSE: Вычисление процента от общего значения.
def calculate_percentage(value: Decimal, total: Decimal) -> Decimal:
    """
    Calculate percentage.
    
    Args:
        value: Value to calculate percentage for
        total: Total value
        
    Returns:
        Percentage as Decimal
    """
    if total == 0:
        return Decimal('0.00')
    return (value / total) * Decimal('100')
# [END_CALCULATE_PERCENTAGE]


# [START_GENERATE_RANDOM_STRING]
# ANCHOR: GENERATE_RANDOM_STRING
# @PreConditions:
# - length положительное целое число (по умолчанию 32)
# @PostConditions:
# - возвращает случайную строку указанной длины из a-zA-Z0-9
# PURPOSE: Генерация криптографически безопасной случайной строки.
def generate_random_string(length: int = 32) -> str:
    """
    Generate a random string.
    
    Args:
        length: Length of the string
        
    Returns:
        Random string
    """
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
# [END_GENERATE_RANDOM_STRING]


# [START_TRUNCATE_STRING]
# ANCHOR: TRUNCATE_STRING
# @PreConditions:
# - text строка для обрезки
# - max_length максимальная длина (по умолчанию 100)
# - suffix суффикс при обрезке (по умолчанию "...")
# @PostConditions:
# - возвращает исходную строку если длина <= max_length
# - иначе обрезанную строку с суффиксом
# PURPOSE: Обрезка строки до заданной длины с добавлением суффикса.
def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
# [END_TRUNCATE_STRING]


# [START_GET_CLIENT_IP]
# ANCHOR: GET_CLIENT_IP
# @PreConditions:
# - request валидный Django HttpRequest объект
# @PostConditions:
# - возвращает IP адрес клиента (из X-Forwarded-For или REMOTE_ADDR)
# PURPOSE: Получение IP адреса клиента из запроса.
def get_client_ip(request) -> str:
    """
    Get client IP address from request.
    
    Args:
        request: Django request object
        
    Returns:
        Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')
# [END_GET_CLIENT_IP]


# === END_CHUNK: CORE_UTILS_V1 ===