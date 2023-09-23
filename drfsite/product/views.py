from django.db import models
from django.db.models import Sum, Count
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import models
from rest_framework.permissions import IsAuthenticated

from .models import Product, UserProductAccess, Lesson, LessonView, User
from .serializers import ProductSerializer, ProductStatisticsSerializer, LessonViewSerializer


class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductStatisticsView(generics.ListAPIView):
    serializer_class = ProductStatisticsSerializer
    queryset = Product.objects.annotate(
        num_lessons_viewed=Count('lessonview'),
        total_time_watched=Sum(models.F('lessonview__end_time') - models.F('lessonview__start_time')),
        num_students=Count('lessonview__user', distinct=True),
        product_percent=(Count('userproductaccess') / User.objects.count()) * 100
    )


class LessonListView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        user_products = UserProductAccess.objects.filter(user=user)
        products = [up.product for up in user_products]
        lessons = Lesson.objects.filter(products__in=products)

        lesson_views = LessonView.objects.filter(user=user, lesson__in=lessons).select_related('lesson', 'product')
        serialized_data = LessonViewSerializer(lesson_views, many=True).data

        return Response(serialized_data)


class LessonViewList(generics.ListAPIView):
    serializer_class = LessonViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        product_id = self.kwargs['product_id']

        return LessonView.objects.filter(user=user, product_id=product_id)


class LessonByProductView(APIView):
    def get(self, request, product_id, *args, **kwargs):
        user = request.user
        lessons = Lesson.objects.filter(products=product_id)

        user_lesson_views = LessonView.objects.filter(user=user, lesson__in=lessons).select_related('lesson', 'product').prefetch_related('user')

        lesson_views = []

        for user_lesson_view in user_lesson_views:
            user_lesson_view_data = LessonViewSerializer(user_lesson_view).data
            user_lesson_view_data['last_watched_time'] = user_lesson_view.end_time
            lesson_views.append(user_lesson_view_data)

        return Response(lesson_views)