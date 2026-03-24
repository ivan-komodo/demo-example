"""
Core pagination for LMS System.

This module contains pagination classes used across all apps.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# === CHUNK: CORE_PAGINATION_V1 [CORE] ===
# Описание: Классы пагинации для API.
# Dependencies: none


# [START_STANDARD_PAGINATION]
# ANCHOR: STANDARD_PAGINATION
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет пагинацию с размером страницы 20 (макс 100)
# PURPOSE: Стандартная пагинация для большинства API endpoints.
class StandardPagination(PageNumberPagination):
    """
    Standard pagination class with configurable page size.
    """
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    # [START_GET_PAGINATED_RESPONSE]
    # ANCHOR: GET_PAGINATED_RESPONSE
    # @PreConditions:
    # - data список сериализованных данных
    # @PostConditions:
    # - возвращает Response с count, next, previous, page_size, results
    # PURPOSE: Формирование ответа с метаданными пагинации.
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
    # [END_GET_PAGINATED_RESPONSE]


# [END_STANDARD_PAGINATION]


# [START_SMALL_PAGINATION]
# ANCHOR: SMALL_PAGINATION
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет пагинацию с размером страницы 10 (макс 50)
# PURPOSE: Малая пагинация для списков с небольшим количеством элементов.
class SmallPagination(PageNumberPagination):
    """
    Small pagination for lists with fewer items.
    """
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
# [END_SMALL_PAGINATION]


# [START_LARGE_PAGINATION]
# ANCHOR: LARGE_PAGINATION
# @PreConditions:
# - нет нетривиальных предусловий для класса
# @PostConditions:
# - предоставляет пагинацию с размером страницы 50 (макс 200)
# PURPOSE: Большая пагинация для списков с множеством элементов.
class LargePagination(PageNumberPagination):
    """
    Large pagination for lists with many items.
    """
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
# [END_LARGE_PAGINATION]


# === END_CHUNK: CORE_PAGINATION_V1 ===