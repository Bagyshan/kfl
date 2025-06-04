from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Количество элементов на странице
    page_size_query_param = 'page_size'  # Позволяет пользователям управлять размером страницы
    max_page_size = 100  # Максимальный размер страницы
