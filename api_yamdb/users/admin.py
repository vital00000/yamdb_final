from django.contrib import admin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'role'
    )
    search_fields = ('username', 'email', 'role')
    list_filter = ('role', )
    empty_value_display = '-_-'
