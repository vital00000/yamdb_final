from datetime import datetime

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=True)

    def validate_username(self, value):
        if value == 'me' or User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Недопустимый username!')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Недопустимый email!')
        return value


class JWTTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User
        read_only_field = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('slug', 'name')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('slug', 'name')


class GetTitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class PostTitleSerializer(serializers.ModelSerializer):
    genre = SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        if value > datetime.now().year:
            raise serializers.ValidationError(
                'Нельзя опубликовать произведение из будущего :)'
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Комментарии к отзывам."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'pub_date', 'text',)


class ReviewSerializer(serializers.ModelSerializer):
    """Отзывы на произведения. """
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)

    def validate_score(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError('Поставьте оценку от 1 до 10')
        return value

    def validate(self, data):
        user = self.context['request'].user
        title_id = (
            self.context.get(
                'request'
            ).parser_context.get('kwargs').get('title_id')
        )
        if self.context['request'].method == 'POST' and (
            Review.objects.filter(author=user, title_id=title_id).exists()
        ):
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение!'
            )
        return data
