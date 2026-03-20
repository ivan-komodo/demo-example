"""
Core pagination for LMS System.

This module contains pagination classes used across all apps.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    Standard pagination class with configurable page size.
    """
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Return paginated response with metadata.
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
            'results': data,
        })


class SmallPagination(PageNumberPagination):
    """
    Small pagination for lists with fewer items.
    """
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class LargePagination(PageNumberPagination):
    """
    Large pagination for lists with many items.
    """
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200