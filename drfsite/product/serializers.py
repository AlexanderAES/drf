from django.db.models import Sum
from rest_framework import serializers, generics
from django.db import models
from .models import Product, Lesson, LessonView, UserProductAccess
from .models import User


class ProductStatisticsSerializer(serializers.ModelSerializer):
    num_lessons_viewed = serializers.SerializerMethodField()
    total_time_watched = serializers.SerializerMethodField()
    num_students = serializers.SerializerMethodField()
    product_percent = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'num_lessons_viewed', 'total_time_watched', 'num_students', 'product_percent')

    def get_num_lessons_viewed(self, obj):
        return LessonView.objects.filter(product=obj).count()

    def get_total_time_watched(self, obj):
        total_time = LessonView.objects.filter(product=obj).aggregate(
            sum_time=Sum(models.F('end_time') - models.F('start_time'))
        )
        return total_time.get('sum_time', 0)

    def get_num_students(self, obj):
        return LessonView.objects.filter(product=obj).values('user').distinct().count()

    def get_product_percent(self, obj):
        total_users = User.objects.count()
        num_users_with_access = UserProductAccess.objects.filter(product=obj).count()
        if total_users > 0:
            return (num_users_with_access / total_users) * 100
        return 0


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class LessonViewSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer()

    class Meta:
        model = LessonView
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

