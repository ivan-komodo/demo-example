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