from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter

from .views import (
    UsersViewSet,
    sent_email,
    YamdbTokenObtainPairView,
    CategoriesViewSet,
    GenresViewSet,
    TitlesViewSet,
    ReviewViewSet,
    CommentViewSet,
)

users_router = DefaultRouter()
users_router.register("", UsersViewSet)

router = DefaultRouter()
router.register("api/v1/categories", CategoriesViewSet)
router.register("api/v1/genres", GenresViewSet)
router.register("api/v1/titles", TitlesViewSet)
router.register(r"api/v1/titles/(?P<title_id>\d+)/reviews", ReviewViewSet)
router.register(
    r"api/v1/titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
)


urlpatterns = [
    path("api/v1/auth/email/", csrf_exempt(sent_email)),
    path("api/v1/auth/token/", YamdbTokenObtainPairView.as_view()),
    path("api/v1/users/", include(users_router.urls)),
    path("", include(router.urls)),
]
