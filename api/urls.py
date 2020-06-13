from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UsersViewSet, UserViewSet, sent_email, YamdbTokenObtainPairView

users_router = DefaultRouter()
users_router.register('', UsersViewSet)
user_router = DefaultRouter()
user_router.register('', UserViewSet)
#user_router.register('', UserViewSet.as_view({'delete': 'destroy'}))


urlpatterns = [
    path('api/v1/auth/email/', csrf_exempt(sent_email)),
    path('api/v1/auth/token/', YamdbTokenObtainPairView.as_view()),
   # path('api/v1/obtain_token/', YamdbTokenObtainPairView.as_view()),
   # path('api/v1/users/<username>/', UserViewSet.as_view({'get': 'retrieve','put': 'update','patch': 'partial_update','delete': 'destroy'})),
    path('api/v1/users/<username>/', include(user_router.urls)),
    path('api/v1/users/', include(users_router.urls)),

]
