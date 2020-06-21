from django_filters import rest_framework as filters
from .models import Titles


class SlugFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__slug', lookup_expr='icontains')
    genre = filters.CharFilter(field_name='genre__slug', lookup_expr='icontains')

    class Meta:
        model = Titles
        fields = ['category', 'genre', 'year', 'name']