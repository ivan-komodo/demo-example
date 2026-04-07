"""
Core utilities for LMS System.

This module contains utility functions used across all apps.
"""

import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger('lms')


# [START_LOG_LINE]
"""
ANCHOR: LOG_LINE
PURPOSE: AI-friendly логирование для автоматического анализа и диагностики ошибок.

@PreConditions:
- module: непустая строка с названием модуля/подсистемы
- level: один из "DEBUG" | "INFO" | "WARN" | "ERROR"
- function_name: непустая строка с названием функции
- anchor: ANCHOR_ID из контракта (UPPER_SNAKE_CASE)
- point: одна из точек ENTRY | EXIT | BRANCH | DECISION | CHECK | ERROR | RETRY | STATE_CHANGE
- data: словарь с контекстными данными

@PostConditions:
- запись лога в structured JSON format
- при ERROR уровне отправка в Sentry (если настроен)

@Invariants:
- формат лога всегда JSON-структурированный
- anchor всегда совпадает с контрактом функции

@SideEffects:
- запись в лог-файл или отправка в Sentry

@ForbiddenChanges:
- формат лога (JSON structured)
- обязательные поля: timestamp, module, level, function_name, anchor, point
"""
def log_line(
    module: str,
    level: str,
    function_name: str,
    anchor: str,
    point: str,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log a structured line for AI-friendly analysis.
    
    Args:
        module: Module/subsystem name (e.g., "users", "courses", "auth")
        level: Log level - "DEBUG", "INFO", "WARN", "ERROR"
        function_name: Name of the function being logged
        anchor: ANCHOR_ID from the contract
        point: Point in function - ENTRY, EXIT, BRANCH, DECISION, CHECK, ERROR, RETRY, STATE_CHANGE
        data: Contextual data dictionary
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "level": level,
        "function": function_name,
        "anchor": anchor,
        "point": point,
        "data": data or {},
    }
    
    log_message = json.dumps(log_entry, ensure_ascii=False, default=str)
    
    if level == "DEBUG":
        logger.debug(log_message)
    elif level == "INFO":
        logger.info(log_message)
    elif level == "WARN":
        logger.warning(log_message)
    elif level == "ERROR":
        logger.error(log_message)
# [END_LOG_LINE]


# === CHUNK: CORE_UTILS_V1 [CORE] ===
# Описание: Утилиты общего назначения для всего проекта.
# Dependencies: none


# [START_SEND_EMAIL]
"""
ANCHOR: SEND_EMAIL
PURPOSE: Отправка email сообщения через Django mail backend.

@PreConditions:
- subject: непустая строка
- message: непустая строка
- recipient_list: непустой список email адресов

@PostConditions:
- возвращает True при успешной отправке
- возвращает False при ошибке (с логированием причины)

@Invariants:
- email всегда отправляется через настроенный backend
- ошибки не пробрасываются выше функции

@SideEffects:
- отправка email через Django mail backend
- запись в лог при ошибке

@ForbiddenChanges:
- fail_silently=False (всегда False для явного контроля ошибок)
"""
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
    log_line("core", "DEBUG", "send_email", "SEND_EMAIL", "ENTRY", {
        "subject": subject[:50],
        "recipients_count": len(recipient_list),
    })
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        log_line("core", "INFO", "send_email", "SEND_EMAIL", "STATE_CHANGE", {
            "action": "email_sent",
            "recipients_count": len(recipient_list),
        })
        log_line("core", "DEBUG", "send_email", "SEND_EMAIL", "EXIT", {"result": "success"})
        return True
    except Exception as e:
        log_line("core", "ERROR", "send_email", "SEND_EMAIL", "ERROR", {
            "reason": "send_failed",
            "error": str(e),
            "subject": subject[:50],
        })
        log_line("core", "DEBUG", "send_email", "SEND_EMAIL", "EXIT", {"result": "failed"})
        return False
# [END_SEND_EMAIL]


# [START_SEND_TEMPLATE_EMAIL]
"""
ANCHOR: SEND_TEMPLATE_EMAIL
PURPOSE: Отправка email по HTML шаблону с текстовой версией.

@PreConditions:
- subject: непустая строка
- template_name: путь к существующему HTML шаблону
- context: словарь с данными для шаблона
- recipient_list: непустой список email адресов

@PostConditions:
- возвращает True при успешной отправке
- возвращает False при ошибке рендеринга или отправки

@Invariants:
- всегда пытается рендерить как HTML так и plain text версии

@SideEffects:
- рендеринг шаблонов
- отправка email

@ForbiddenChanges:
- попытка найти .txt версию шаблона (fallback механизм)
"""
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
    log_line("core", "DEBUG", "send_template_email", "SEND_TEMPLATE_EMAIL", "ENTRY", {
        "template": template_name,
        "recipients_count": len(recipient_list),
    })
    
    try:
        html_message = render_to_string(template_name, context)
        plain_message = render_to_string(template_name.replace('.html', '.txt'), context)
        
        result = send_email(
            subject=subject,
            message=plain_message,
            recipient_list=recipient_list,
            html_message=html_message,
            from_email=from_email,
        )
        log_line("core", "DEBUG", "send_template_email", "SEND_TEMPLATE_EMAIL", "EXIT", {
            "result": "success" if result else "failed",
        })
        return result
    except Exception as e:
        log_line("core", "ERROR", "send_template_email", "SEND_TEMPLATE_EMAIL", "ERROR", {
            "reason": "template_error",
            "error": str(e),
            "template": template_name,
        })
        log_line("core", "DEBUG", "send_template_email", "SEND_TEMPLATE_EMAIL", "EXIT", {
            "result": "failed",
        })
        return False
# [END_SEND_TEMPLATE_EMAIL]


# [START_FORMAT_CURRENCY]
"""
ANCHOR: FORMAT_CURRENCY
PURPOSE: Форматирование суммы как валюты для отображения.

@PreConditions:
- amount: валидное Decimal значение

@PostConditions:
- возвращает строку формата "1,234.56 RUB"

@Invariants:
- формат всегда с двумя знаками после запятой

@SideEffects:
- нет побочных эффектов

@ForbiddenChanges:
- формат вывода (два знака после запятой)
"""
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
"""
ANCHOR: CALCULATE_PERCENTAGE
PURPOSE: Вычисление процента value от total.

@PreConditions:
- value: валидное Decimal значение
- total: валидное Decimal значение

@PostConditions:
- при total=0 возвращает Decimal('0.00')
- иначе возвращает (value / total) * 100

@Invariants:
- результат всегда типа Decimal
- никогда не выбрасывает ZeroDivisionError

@SideEffects:
- нет побочных эффектов

@ForbiddenChanges:
- защита от деления на ноль (возврат 0 при total=0)
"""
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
"""
ANCHOR: GENERATE_RANDOM_STRING
PURPOSE: Генерация криптографически безопасной случайной строки.

@PreConditions:
- length: положительное целое число

@PostConditions:
- возвращает строку длины length из символов a-zA-Z0-9

@Invariants:
- всегда использует secrets.choice для криптографической безопасности

@SideEffects:
- нет побочных эффектов

@ForbiddenChanges:
- использование secrets вместо random (безопасность)
"""
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
"""
ANCHOR: TRUNCATE_STRING
PURPOSE: Обрезка строки до заданной длины с добавлением суффикса.

@PreConditions:
- text: строка для обрезки
- max_length: максимальная длина результата (по умолчанию 100)
- suffix: суффикс при обрезке (по умолчанию "...")

@PostConditions:
- при len(text) <= max_length возвращает text без изменений
- иначе возвращает обрезанную строку + suffix длиной max_length

@Invariants:
- длина результата всегда <= max_length

@SideEffects:
- нет побочных эффектов

@ForbiddenChanges:
- длина суффикса учитывается при обрезке
"""
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
"""
ANCHOR: GET_CLIENT_IP
PURPOSE: Получение IP адреса клиента из HTTP запроса.

@PreConditions:
- request: валидный Django HttpRequest объект

@PostConditions:
- возвращает IP из X-Forwarded-For (первый в списке) если есть
- иначе возвращает REMOTE_ADDR
- при отсутствии обоих возвращает пустую строку

@Invariants:
- всегда возвращает строку (никогда None)

@SideEffects:
- нет побочных эффектов

@ForbiddenChanges:
- приоритет X-Forwarded-For над REMOTE_ADDR (для прокси)
"""
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