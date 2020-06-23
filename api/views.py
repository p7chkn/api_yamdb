import hashlib
from rest_framework import viewsets, status, permissions, filters
from django.http import HttpResponse
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Categories, Genres, Titles, Review, Comments
from .serializers import (
    UserSerializer,
    YamdbTokenObtainPairSerializer,
    CategoriesSerializer,
    GenresSerializer,
    TitlesSerializer,
    CommentsSerializer,
    ReviewSerializer,
)
from .permissions import IsAdmin, IsAdminOrReadOnly, MethodPermissions
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import TitlesFilter


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        IsAdmin,
    ]
    pagination_class = StandardResultsSetPagination
    lookup_field = "username"

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset)
        self.check_object_permissions(self.request, obj)
        print(obj)
        return obj

    def get_queryset(self, username=None):
        try:
            usename = self.kwargs["username"]
        except Exception:
            queryset = User.objects.all()
            return queryset
        if usename == "me":
            queryset = User.objects.filter(email=self.request.user.email)
            return queryset

        queryset = User.objects.filter(username=usename)
        return queryset

    def destroy(self, request, username=None):
        if username is None or username == "me":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        user = get_object_or_404(User, username=username)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def sent_email(request):
    if request.method == "POST":
        try:
            email = request.POST["email"]
            validate_email(email)
        except Exception:
            return HttpResponse("enter a valid email")
        if User.objects.filter(email=email).first():
            return HttpResponse("This email already register")
        hash_email = hashlib.sha256(email.encode("utf-8")).hexdigest()
        send_mail(
            "Confirm_registration",
            f"Your conformation code is {hash_email}",
            "yamdb@yandex.ru",
            [email,],
            fail_silently=False,
        )
        return HttpResponse(
            "check your mail for conformation code and go to /api/v1/auth/token/ for complete registration"
        )
    return HttpResponse("please, sent email with post request")


class YamdbTokenObtainPairView(TokenObtainPairView):
    serializer_class = YamdbTokenObtainPairSerializer


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [IsAdminOrReadOnly, MethodPermissions]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']
    lookup_field = "slug"


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly,  MethodPermissions]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']
    lookup_field = "slug"


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_title(self):
        title = get_object_or_404(Titles, pk=self.kwargs.get("title_id"))
        return title

    def get_queryset(self):
        queryset = Review.objects.filter(title=self.get_title()).all()
        return queryset

    def partial_update(self, request, title_id, pk=None):
        review = get_object_or_404(Review, pk=pk)
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if review.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if serializer.is_valid():
            serializer.save(author=request.user, title_id=title_id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, title_id, pk=None):
        review = get_object_or_404(Review, pk=pk)
        if review.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        review.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        title = get_object_or_404(Titles, pk=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title_id=self.kwargs.get("title_id"))


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    def get_review(self):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        return review

    def get_queryset(self):
        queryset = Comments.objects.filter(review=self.get_review()).all()
        return queryset

    def partial_update(self, request, title_id, review_id, pk=None):
        comment = get_object_or_404(Comments, pk=pk)
        serializer = CommentsSerializer(comment, data=request.data, partial=True)
        if comment.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if serializer.is_valid():
            serializer.save(author=request.user, review_id=review_id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, title_id, review_id, pk=None):
        comment = get_object_or_404(Comments, pk=pk)
        if comment.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        serializer.save(author=self.request.user, review_id=self.kwargs.get("review_id"))
