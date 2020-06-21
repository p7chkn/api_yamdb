import hashlib
from rest_framework import viewsets, status, filters
from django.http import HttpResponse
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.views import TokenObtainPairView
import django_filters
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import SlugFilter
from .models import User, Categories, Genres, Titles, Review, Comments
from .serializers import UserSerializer, YamdbTokenObtainPairSerializer, CategoriesSerializer, GenresSerializer, \
    TitlesSerializer, ReviewSerializer, CommentsSerializer
from .permissions import IsAdmin, IsAdminOrReadOnly


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin, ]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'username'

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset)
        self.check_object_permissions(self.request, obj)
        print(obj)
        return obj

    def get_queryset(self, username=None):
        try:
            usename = self.kwargs['username']
        except Exception:
            queryset = User.objects.all()
            return queryset
        if usename == 'me':
            queryset = User.objects.filter(email=self.request.user.email)
            return queryset

        queryset = User.objects.filter(username=usename)
        return queryset

    def destroy(self, request, username=None):
        if username is None or username == 'me':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        user = get_object_or_404(User, username=username)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def sent_email(request):
    if request.method == 'POST':
        try:
            email = request.POST['email']
            validate_email(email)
        except Exception:
            return HttpResponse('enter a valid email')
        if User.objects.filter(email=email).first():
            return HttpResponse('This email already register')
        hash_email = hashlib.sha256(email.encode('utf-8')).hexdigest()
        send_mail(
                    'Confirm_registration',
                    f'Your conformation code is {hash_email}',
                    'yamdb@yandex.ru',
                    [email, ],
                    fail_silently=False,)
        return HttpResponse('check your mail for conformation code and go to /api/v1/auth/token/ for complete registration')
    return HttpResponse('please, sent email with post request')


class YamdbTokenObtainPairView(TokenObtainPairView):
    serializer_class = YamdbTokenObtainPairSerializer


class CategoriesView(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [ IsAdminOrReadOnly, ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Categories.objects.all()
        name = self.request.query_params.get("name")
        if name is not None:
            queryset = queryset.filter(id=name)
        return queryset

    def destroy(self, request, slug=None):
        if slug is None:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        slug = get_object_or_404(Categories, slug=slug)
        slug.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenresView(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]
    lookup_field = 'slug'


class TitlesView(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = SlugFilter



class ReviewView(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        title = get_object_or_404(Titles, pk=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title_id=self.kwargs.get("title_id"))


class CommentsView(viewsets.ModelViewSet):
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    pagination_class = StandardResultsSetPagination

    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title_id=self.kwargs.get("title_id"),
            review_id=self.kwargs.get("review_id"),
        )