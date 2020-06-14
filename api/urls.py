from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter

from .views import UsersViewSet, sent_email, YamdbTokenObtainPairView

users_router = DefaultRouter()
users_router.register('', UsersViewSet)


urlpatterns = [
    path('api/v1/auth/email/', csrf_exempt(sent_email)),
    path('api/v1/auth/token/', YamdbTokenObtainPairView.as_view()),
    path('api/v1/users/', include(users_router.urls)),

]
