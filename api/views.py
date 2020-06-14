import hashlib
from rest_framework import viewsets, status
from django.http import HttpResponse
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import UserSerializer, YamdbTokenObtainPairSerializer
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
