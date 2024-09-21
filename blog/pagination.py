# pagination.py

from rest_framework.pagination import PageNumberPagination

class PostPagination(PageNumberPagination):
    page_size = 5  # Number of posts per page
    page_query_param = 'pageno' 
    page_size_query_param = 'page_size'  # Optional: allows clients to set the page size via a query parameter
    max_page_size = 100  # Optional: maximum page size that clients can request
