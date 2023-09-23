from django.urls import path
from .views import ProductList, ProductStatisticsView, LessonListView, LessonViewList, LessonByProductView

urlpatterns = [
    path('products/', ProductList.as_view(), name='product_list'),
    path('products-stats/', ProductStatisticsView.as_view(), name='product_statistics'),
    path('lessons/', LessonListView.as_view(), name='lesson_list'),
    path('products/<int:product_id>/lessons/', LessonViewList.as_view(), name='lesson_list'),
    path('lessons/by_product/<int:product_id>/', LessonByProductView.as_view(), name='lesson-by-product'),
]