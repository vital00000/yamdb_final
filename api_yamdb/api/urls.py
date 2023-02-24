from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet, UserViewSet,
                       obtain_jwt_token, send_confirmation_code)
from django.urls import include, path
from rest_framework import routers

app_name = 'api'

v1_router = routers.DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='user')
v1_router.register(r'categories', CategoryViewSet, basename='category')
v1_router.register(r'genres', GenreViewSet, basename='genre')
v1_router.register(r'titles', TitleViewSet, basename='title')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comment'
)

auth_urls = [
    path('signup/', send_confirmation_code),
    path('token/', obtain_jwt_token),
]

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/', include(auth_urls)),
]
