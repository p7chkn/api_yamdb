from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter

from .views import UsersViewSet, sent_email, YamdbTokenObtainPairView, CategoriesView, GenresView, TitlesView, ReviewView, CommentsView

users_router = DefaultRouter()
users_router.register('', UsersViewSet)

router = DefaultRouter()
# router.register('api/v1/categories', CategoriesView)
router.register(r'api/v1/categories', CategoriesView)
router.register(r'api/v1/categories', CategoriesView)
router.register('api/v1/genres', GenresView)
router.register('api/v1/titles', TitlesView)


router.register(r"api/v1/titles/(?P<titles_id>\d+)/reviews", ReviewView, basename="review")
router.register(r"api/v1/titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments", CommentsView, basename="comments")

urlpatterns = [
    path('api/v1/auth/email/', csrf_exempt(sent_email)),
    path('api/v1/auth/token/', YamdbTokenObtainPairView.as_view()),
    path('api/v1/users/', include(users_router.urls)),
    path('', include(router.urls)),
]