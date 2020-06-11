from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UsersViewSet, UserViewSet

users_router = DefaultRouter()
users_router.register('', UsersViewSet)
user_router = DefaultRouter()
user_router.register('', UserViewSet)


urlpatterns = [
    path('api/v1/auth/token/', TokenObtainPairView.as_view()),
    path('api/v1/users/<username>/', include(user_router.urls)),
    path('api/v1/users/', include(users_router.urls)),
    
]
