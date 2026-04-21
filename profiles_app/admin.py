from django.contrib import admin

from profiles_app.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'user_type', 'created_at')
    list_filter = ('user_type',)
    search_fields = ('user__username', 'user__email')
