from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book/add/', views.add_book, name='add_book'),
    path('book/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('book/find-closest/', views.find_closest_book, name='find_closest_book'),
    path('stats/color-flips/', views.color_flip_count, name='color_flip_count'),
]