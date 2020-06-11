from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_list_or_404
from .models import User
from .serializers import UserSerializer
from .permissions import IsAdmin


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin, ]
    pagination_class = StandardResultsSetPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin, ]

    def get_queryset(self):
        return User.objects.filter(username=self.kwargs['username'])
