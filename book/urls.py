from django.urls import path
from .views.fbv import book_list, book_detail

from .views.user_permission import BookListCreateView

urlpatterns = [
    path('', BookListCreateView.as_view(), name='book-list-create'),
]

urlpatterns += [
    path('books/', book_list, name='book-list'),
    path('books/<int:pk>/', book_detail, name='book-detail'),
]

# urls.py

from .views.generic_apiview import (
    BookListCreateView,
    BookRetrieveView,
    BookUpdateView,
    BookDestroyView,
    BookRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('generic/books/', BookListCreateView.as_view(), name='book-list-create'),
    path('generic/books/<int:pk>/', BookRetrieveView.as_view(), name='book-retrieve'),
    path('generic/books/<int:pk>/update/', BookUpdateView.as_view(), name='book-update'),
    path('generic/books/<int:pk>/delete/', BookDestroyView.as_view(), name='book-delete'),
    path('generic/books/<int:pk>/detail/', BookRetrieveUpdateDestroyView.as_view(), name='book-detail'),
]
