import hashlib
from rest_framework import viewsets
from django.http import HttpResponse
from django.core.validators import validate_email
from django.core.mail import send_mail
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin, ]

    def get_queryset(self):
        return User.objects.filter(username=self.kwargs['username'])


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
