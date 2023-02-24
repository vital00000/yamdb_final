from api.filters import TitleFilter
from api.permissions import (IsAdminOrModeratorOrAuthorOrReadOnly,
                             IsAdminOrReadOnly, IsAdminOrSuperuser)
from api.serializers import (CategorySerializer, CommentSerializer,
                             ConfirmationCodeSerializer, GenreSerializer,
                             GetTitleSerializer, JWTTokenSerializer,
                             PostTitleSerializer, ReviewSerializer,
                             UserSerializer)
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title
from users.models import User


class PostListDelete(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    serializer = ConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_email = serializer.validated_data.get('email')
    user, _ = User.objects.get_or_create(
        username=serializer.validated_data.get('username'),
        email=user_email,
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Yamdb confirmation code',
        f'Use this code to get a token:{confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False
    )
    return Response(
        {
            'email': user_email,
            'username': user.username
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_jwt_token(request):
    serializer = JWTTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data.get('username')
    )
    if default_token_generator.check_token(
        user,
        serializer.validated_data.get('confirmation_code')
    ):
        jwt_token = AccessToken.for_user(user)
        return Response(
            {
                'jwt_token': (
                    f'Use this token to get access to api: {str(jwt_token)}'
                )
            },
            status=status.HTTP_200_OK
        )
    return Response(
        {'confirmation_code': 'Incorrect confirmation code!'},
        status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdminOrSuperuser, )

    @action(
        detail=False,
        methods=['patch', 'get'],
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        user = self.request.user
        if self.request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
        return Response(
            self.get_serializer(user).data, status=status.HTTP_200_OK
        )


class CategoryViewSet(PostListDelete):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(PostListDelete):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by('-year')
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetTitleSerializer
        return PostTitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Комментарии к отзывам.
    Комментарий привязан к определённому отзыву."""
    serializer_class = CommentSerializer
    permission_classes = (
        IsAdminOrModeratorOrAuthorOrReadOnly,
    )

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get("review_id"),
            title__id=self.kwargs.get("title_id")
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get("review_id"),
            title__id=self.kwargs.get("title_id")
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=self.request.user,
            review=review,
            title=get_object_or_404(Title, id=self.kwargs.get("title_id"))
        )


class ReviewViewSet(viewsets.ModelViewSet):
    """Отзывы на произведения.
    Отзыв привязан к определённому произведению.
    """
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAdminOrModeratorOrAuthorOrReadOnly,
    )

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=self.request.user,
            title=title
        )
