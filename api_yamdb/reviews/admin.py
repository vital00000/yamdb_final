from django.contrib import admin
from reviews.models import Category, Comment, Genre, Review, Title


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'category',
        'year',
        'description'
    )
    search_fields = ('name',)
    list_filter = ('year', 'category', 'genre')
    empty_value_display = '-_-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-_-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-_-'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'text',
        'score',
        'author',
        'pub_date',
    )
    search_fields = ('text',)
    list_filter = ('author', 'score')
    empty_value_display = '-_-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'review',
        'text',
        'author',
        'pub_date',
    )
    search_fields = ('text',)
    list_filter = ('review', 'author')
    empty_value_display = '-_-'
